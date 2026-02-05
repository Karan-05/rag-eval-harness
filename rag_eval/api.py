import asyncio

from fastapi import FastAPI

from .evaluator import Evaluator

app = FastAPI(title="RAG Eval Harness", version="0.1.0")


@app.on_event("shutdown")
async def shutdown_event():
	app.state.evaluator.close()


@app.on_event("startup")
async def startup_event():
	app.state.evaluator = Evaluator()


@app.post("/evals/run")
async def run_eval(async_mode: bool = False):
	evaluator: Evaluator = app.state.evaluator
	if async_mode:
		result = await evaluator.run_async()
	else:
		result = await asyncio.get_event_loop().run_in_executor(None, evaluator.run)
	return result


@app.get("/healthz")
async def health():
	return {"status": "ok"}
