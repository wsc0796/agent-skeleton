from src.tools.builtin import calculator, read_file


class TestCalculatorSecurity:
    def test_basic_arithmetic(self):
        result = calculator("2 + 3")
        assert result["result"] == 5

    def test_complex_expression(self):
        result = calculator("2 + 3 * 4")
        assert result["result"] == 14

    def test_parentheses(self):
        result = calculator("(2 + 3) * 4")
        assert result["result"] == 20

    def test_division(self):
        result = calculator("10 / 3")
        assert abs(result["result"] - 3.333) < 0.01

    def test_negative(self):
        result = calculator("-5 + 3")
        assert result["result"] == -2

    def test_division_by_zero_is_caught(self):
        result = calculator("1 / 0")
        assert "error" in result

    def test_code_injection_blocked(self):
        result = calculator("__import__('os').system('dir')")
        assert "error" in result

    def test_eval_attack_blocked(self):
        result = calculator("open('.env').read()")
        assert "error" in result


class TestReadFileSecurity:
    def test_env_blocked(self):
        result = read_file(".env")
        assert "Access denied" in result["error"]

    def test_dotdot_blocked(self):
        result = read_file("../secret.txt")
        assert "Access denied" in result["error"]

    def test_absolute_path_blocked(self):
        result = read_file("C:\\Windows\\System32\\config\\SAM")
        assert "Access denied" in result["error"]

    def test_nonexistent_file(self):
        result = read_file("./examples/nonexistent.txt")
        assert "File not found" in result["error"]
