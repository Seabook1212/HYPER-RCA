#!/usr/bin/env python3
"""Record a future run's actual LLM I/O without changing its RCA algorithm.

Uses the existing LLMClient._log_io transport hook. Running this wrapper can
make paid API calls, exactly as running examples/run_csv_mode.py directly does.
"""
from contextlib import contextmanager
from datetime import datetime, timezone
from functools import wraps
import argparse
import json
from pathlib import Path
import runpy
import sys
from threading import Lock, local
from time import perf_counter


class TraceRecorder:
    SETTINGS = (
        "max_output_tokens", "max_tokens", "thinking_level", "thinking_budget",
        "thinking_budget_2_5", "reasoning_effort", "verbosity", "top_p", "top_k",
        "seed", "enforce_response_schema", "include_temperature", "max_retries",
        "min_request_interval_sec", "timeout_sec",
    )
    SECRET_KEYS = {"api_key", "authorization", "access_token", "refresh_token", "password", "client_secret"}

    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.stream = path.open("x", encoding="utf-8", buffering=1)
        self.lock = Lock()
        self.state = local()
        self.sequence = 0
        self.call_count = 0
        self.started = perf_counter()

    @classmethod
    def scrub(cls, value):
        if isinstance(value, dict):
            return {k: "<REDACTED>" if str(k).lower() in cls.SECRET_KEYS else cls.scrub(v)
                    for k, v in value.items()}
        if isinstance(value, list):
            return [cls.scrub(v) for v in value]
        return value

    def emit(self, event, **fields):
        with self.lock:
            self.sequence += 1
            record = dict(sequence=self.sequence, event=event,
                          timestamp_utc=datetime.now(timezone.utc).isoformat(),
                          elapsed_sec=perf_counter() - self.started, **fields)
            self.stream.write(json.dumps(self.scrub(record), ensure_ascii=False, default=str) + "\n")

    @contextmanager
    def install(self, client_class):
        original_generate = client_class.generate_json
        original_log = client_class._log_io
        recorder = self

        @wraps(original_generate)
        def generate(client, system_prompt, payload, purpose):
            with recorder.lock:
                recorder.call_count += 1
                call_id = f"call-{recorder.call_count:04d}"
            previous = getattr(recorder.state, "current", None)
            recorder.state.current = dict(call_id=call_id, purpose=purpose, attempt=0)
            options = client._provider_config(client.provider)
            recorder.emit("call_start", call_id=call_id, purpose=purpose,
                          provider=client.provider, model=client.model,
                          configured_temperature=client.temperature,
                          explicit_provider_settings={k: options[k] for k in recorder.SETTINGS if k in options})
            try:
                output = original_generate(client, system_prompt, payload, purpose)
                recorder.emit("call_end", call_id=call_id, purpose=purpose,
                              returned_type=type(output).__name__,
                              note="An empty dict may be a provider/format fallback; inspect result call records.")
                return output
            except BaseException as exc:
                recorder.emit("call_exception", call_id=call_id, purpose=purpose,
                              exception_type=type(exc).__name__)
                raise
            finally:
                recorder.state.current = previous

        @wraps(original_log)
        def log_io(client, purpose, direction, payload):
            state = getattr(recorder.state, "current", None)
            if state is None:
                raise RuntimeError("LLM transport hook called outside a recorded logical call")
            if direction == "INPUT":
                state["attempt"] += 1
            recorder.emit("request" if direction == "INPUT" else "response",
                          call_id=state["call_id"], purpose=purpose,
                          attempt=state["attempt"], payload=payload)
            return original_log(client, purpose, direction, payload)

        client_class.generate_json = generate
        client_class._log_io = log_io
        try:
            yield
        finally:
            client_class.generate_json = original_generate
            client_class._log_io = original_log

    def close(self):
        self.stream.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-project", type=Path, required=True)
    parser.add_argument("--trace-file", type=Path, required=True,
                        help="New JSONL file; existing files are never overwritten")
    parser.add_argument("runner_args", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    source = args.source_project.expanduser().resolve()
    runner = source / "examples/run_csv_mode.py"
    if not runner.is_file():
        parser.error("source-project must contain examples/run_csv_mode.py")
    runner_args = args.runner_args[1:] if args.runner_args[:1] == ["--"] else args.runner_args
    sys.path.insert(0, str(source / "src"))
    from rca_agent_skills.llm.client import LLMClient
    recorder = TraceRecorder(args.trace_file.expanduser().resolve())
    recorder.emit("session_start", runner="examples/run_csv_mode.py",
                  capture_scope="Actual application-level requests and logged raw model text; not full HTTP/SDK envelopes",
                  source_client_sha256=__import__("hashlib").sha256(
                      (source / "src/rca_agent_skills/llm/client.py").read_bytes()).hexdigest())
    previous_argv = sys.argv
    ok = False
    try:
        sys.argv = [str(runner), *runner_args]
        with recorder.install(LLMClient):
            runpy.run_path(str(runner), run_name="__main__")
        ok = True
    finally:
        sys.argv = previous_argv
        recorder.emit("session_end", success=ok, logical_calls_started=recorder.call_count)
        recorder.close()


if __name__ == "__main__":
    main()
