from mcp.server.fastmcp import FastMCP

# Initialize FastMCP
mcp = FastMCP("Math") # "Math" is the name of the MCP server

@mcp.tool()
def add(a: int, b: int) -> int:
    """
    Add two numbers
    Args:
        a (int): First number
        b (int): Second number
    Returns:
        int: Sum of a and b
    """
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """
    Multiply two numbers
    Args:
        a (int): First number
        b (int): Second number
    Returns:
        int: Result of multiplication
    """
    return a * b

@mcp.tool()
def calculate(expression: str) -> str:
    """
    Evaluate a safe arithmetic expression and return the result.
    Use this for any multi-step or compound math problem.
    Args:
        expression (str): A math expression using +, -, *, /, (, ) and numbers.
                          Example: '(10 + 4) * 67'
    Returns:
        str: The result of the expression
    """
    import ast, operator

    allowed_ops = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
    }

    def _eval(node):
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.BinOp):
            op_fn = allowed_ops.get(type(node.op))
            if op_fn is None:
                raise ValueError(f"Unsupported operator: {node.op}")
            return op_fn(_eval(node.left), _eval(node.right))
        elif isinstance(node, ast.UnaryOp):
            op_fn = allowed_ops.get(type(node.op))
            if op_fn is None:
                raise ValueError(f"Unsupported operator: {node.op}")
            return op_fn(_eval(node.operand))
        else:
            raise ValueError(f"Unsupported expression node: {node}")

    try:
        tree = ast.parse(expression, mode="eval")
        result = _eval(tree.body)
        return f"Result of '{expression}' = {result}"
    except Exception as e:
        return f"Error evaluating expression: {e}"


# To start the server, run this script.
# The server will run on http://[IP_ADDRESS]/mcp
if __name__ == "__main__":
    mcp.run(transport="stdio") # other options are "http", "sse", "sse", "websocket"
                               # "stdio" --> This is used for the CLI tool mcp, you can also use it for VS Code / Antigravity