import ast
import json
import logging
import operator
import sqlite3

import boto3

MODEL_ID = "us.anthropic.claude-sonnet-4-6"
MAX_ITERATIONS = 6

bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')

# Task 4: detailed logging of model decisions (console + agent.log)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%H:%M:%S",
    handlers=[logging.StreamHandler(), logging.FileHandler("agent.log", mode="w")],
)
log = logging.getLogger("agent")

# Tools (Task 2)

OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
       ast.Div: operator.truediv, ast.Pow: operator.pow, ast.USub: operator.neg}


def calculator(expression):
    def ev(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in OPS:
            return OPS[type(node.op)](ev(node.left), ev(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in OPS:
            return OPS[type(node.op)](ev(node.operand))
        raise ValueError("Unsupported expression")
    return str(ev(ast.parse(expression, mode="eval").body))


def web_search(query):
    """Simulated search: returns canned results (no real internet access)."""
    fake_web = {
        "lambda": "AWS Lambda: serverless compute, max timeout 15 minutes, memory 128 MB to 10,240 MB.",
        "bedrock": "Amazon Bedrock: managed service for foundation models through a single API.",
        "s3": "Amazon S3: object storage, 99.999999999% durability, objects up to 5 TB.",
    }
    hits = [text for key, text in fake_web.items() if key in query.lower()]
    return "\n".join(hits) if hits else "No results found."


db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE employees (name TEXT, team TEXT, salary REAL)")
db.executemany("INSERT INTO employees VALUES (?, ?, ?)", [
    ("Ana", "Data", 9000), ("Bruno", "Data", 8000), ("Carla", "Cloud", 11000),
    ("Diego", "Cloud", 10000), ("Elisa", "Cloud", 9500),
])


def query_database(sql):
    if not sql.strip().lower().startswith("select"):
        return "Error: only SELECT queries are allowed."
    rows = db.execute(sql).fetchall()
    return json.dumps(rows)


TOOLS = {"calculator": calculator, "web_search": web_search, "query_database": query_database}

TOOL_CONFIG = {"tools": [
    {"toolSpec": {
        "name": "calculator",
        "description": "Evaluate a math expression, e.g. '(9000 + 8000) / 2'.",
        "inputSchema": {"json": {"type": "object", "properties": {
            "expression": {"type": "string"}}, "required": ["expression"]}}}},
    {"toolSpec": {
        "name": "web_search",
        "description": "Search the web for information about AWS services.",
        "inputSchema": {"json": {"type": "object", "properties": {
            "query": {"type": "string"}}, "required": ["query"]}}}},
    {"toolSpec": {
        "name": "query_database",
        "description": "Run a SELECT query on the table employees(name, team, salary).",
        "inputSchema": {"json": {"type": "object", "properties": {
            "sql": {"type": "string"}}, "required": ["sql"]}}}},
]}

# Agent loop (Tasks 1 and 3)


def run_agent(question):
    log.info(f"QUESTION: {question}")
    messages = [{"role": "user", "content": [{"text": question}]}]

    for step in range(1, MAX_ITERATIONS + 1):
        response = bedrock_runtime.converse(
            modelId=MODEL_ID,
            messages=messages,
            toolConfig=TOOL_CONFIG,
            inferenceConfig={"maxTokens": 800, "temperature": 0},
        )
        message = response['output']['message']
        messages.append(message)
        usage = response['usage']
        log.info(f"[step {step}] stop_reason={response['stopReason']} "
                 f"tokens in/out={usage['inputTokens']}/{usage['outputTokens']}")

        if response['stopReason'] != 'tool_use':
            answer = "".join(b.get('text', '') for b in message['content'])
            log.info(f"[step {step}] FINAL ANSWER: {answer}\n")
            return answer

        results = []
        for block in message['content']:
            if 'text' in block:
                log.info(f"[step {step}] model says: {block['text']}")
            if 'toolUse' in block:
                tool = block['toolUse']
                log.info(f"[step {step}] DECISION: call {tool['name']}({json.dumps(tool['input'])})")
                try:
                    output = TOOLS[tool['name']](**tool['input'])
                    status = "success"
                except Exception as e:
                    output, status = f"Error: {e}", "error"
                log.info(f"[step {step}] RESULT ({status}): {output}")
                results.append({"toolResult": {
                    "toolUseId": tool['toolUseId'],
                    "content": [{"text": output}],
                    "status": status}})
        messages.append({"role": "user", "content": results})

    log.info("Stopped: reached MAX_ITERATIONS\n")
    return "Stopped: too many steps."


if __name__ == "__main__":
    run_agent("What is 15% of 2480?")
    run_agent("Which team has the highest average salary, and how much higher is it than the other team's average?")
    run_agent("What is the maximum timeout of AWS Lambda in seconds, and how many employees are in the Cloud team?")
