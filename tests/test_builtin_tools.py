
from src.tools.builtin import builtin_tools, calculator, get_current_time, web_search


class TestBuiltinTools:
    def test_all_tools_have_valid_schemas(self):
        tools = builtin_tools()
        assert len(tools) >= 4

        for tool in tools:
            schema = tool.to_openai_schema()
            assert "function" in schema
            assert schema["function"]["name"] == tool.name

    def test_web_search(self):
        result = web_search("Python")
        assert result["query"] == "Python"
        assert "results" in result

    def test_calculator(self):
        result = calculator("2 + 3 * 4")
        assert result["result"] == 14

    def test_calculator_error(self):
        result = calculator("1/0")
        assert "error" in result

    def test_get_current_time(self):
        result = get_current_time()
        assert "utc_time" in result
