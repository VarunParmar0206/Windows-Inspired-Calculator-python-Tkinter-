import tkinter as tk
from tkinter import ttk
import math
from decimal import Decimal, getcontext
from datetime import datetime, timedelta
import re
from enum import Enum

# Set high precision for calculations
getcontext().prec = 50


class CalculatorMode(Enum):
    STANDARD = "Standard"
    SCIENTIFIC = "Scientific"
    PROGRAMMER = "Programmer"
    DATE = "Date Calculation"
    CONVERTER = "Converter"
    GRAPHING = "Graphing"


class MathEngine:
    """Core calculation engine with expression evaluation"""
    
    def __init__(self):
        self.memory = Decimal('0')
        self.history = []
        
    def evaluate(self, expression):
        """Safely evaluate mathematical expression"""
        try:
            # Replace operators for Python evaluation
            expr = expression.replace('×', '*').replace('÷', '/')
            expr = expr.replace('π', str(math.pi)).replace('e', str(math.e))
            
            # Handle special functions
            expr = self._process_functions(expr)
            
            result = eval(expr, {"__builtins__": {}}, {
                "sin": math.sin, "cos": math.cos, "tan": math.tan,
                "asin": math.asin, "acos": math.acos, "atan": math.atan,
                "sinh": math.sinh, "cosh": math.cosh, "tanh": math.tanh,
                "asinh": math.asinh, "acosh": math.acosh, "atanh": math.atanh,
                "log": math.log, "log10": math.log10, "sqrt": math.sqrt,
                "exp": math.exp, "pow": pow, "abs": abs,
                "factorial": math.factorial, "pi": math.pi, "e": math.e
            })
            
            return Decimal(str(result))
        except Exception as e:
            raise ValueError(f"Invalid expression: {e}")
    
    def _process_functions(self, expr):
        """Process special calculator functions"""
        # Handle x² as x**2
        expr = re.sub(r'(\d+)²', r'\1**2', expr)
        # Handle √x as sqrt(x)
        expr = re.sub(r'√\(([^)]+)\)', r'sqrt(\1)', expr)
        return expr
    
    def add_to_memory(self, value):
        self.memory += Decimal(str(value))
    
    def subtract_from_memory(self, value):
        self.memory -= Decimal(str(value))
    
    def recall_memory(self):
        return self.memory
    
    def clear_memory(self):
        self.memory = Decimal('0')
    
    def store_memory(self, value):
        self.memory = Decimal(str(value))


class ConversionService:
    """Handles unit conversions for various categories"""
    
    CONVERSIONS = {
        "Length": {
            "units": ["Meters", "Kilometers", "Centimeters", "Millimeters", "Miles", "Yards", "Feet", "Inches"],
            "to_base": {  # Convert to meters
                "Meters": 1, "Kilometers": 1000, "Centimeters": 0.01, "Millimeters": 0.001,
                "Miles": 1609.344, "Yards": 0.9144, "Feet": 0.3048, "Inches": 0.0254
            }
        },
        "Weight": {
            "units": ["Kilograms", "Grams", "Milligrams", "Pounds", "Ounces", "Tons"],
            "to_base": {  # Convert to kilograms
                "Kilograms": 1, "Grams": 0.001, "Milligrams": 0.000001,
                "Pounds": 0.453592, "Ounces": 0.0283495, "Tons": 1000
            }
        },
        "Temperature": {
            "units": ["Celsius", "Fahrenheit", "Kelvin"],
            "special": True  # Temperature needs special conversion logic
        },
        "Volume": {
            "units": ["Liters", "Milliliters", "Gallons", "Quarts", "Pints", "Cups", "Fluid Ounces"],
            "to_base": {  # Convert to liters
                "Liters": 1, "Milliliters": 0.001, "Gallons": 3.78541, "Quarts": 0.946353,
                "Pints": 0.473176, "Cups": 0.236588, "Fluid Ounces": 0.0295735
            }
        },
        "Time": {
            "units": ["Seconds", "Minutes", "Hours", "Days", "Weeks", "Years"],
            "to_base": {  # Convert to seconds
                "Seconds": 1, "Minutes": 60, "Hours": 3600, "Days": 86400,
                "Weeks": 604800, "Years": 31536000
            }
        },
        "Speed": {
            "units": ["Meters/second", "Kilometers/hour", "Miles/hour", "Feet/second", "Knots"],
            "to_base": {  # Convert to m/s
                "Meters/second": 1, "Kilometers/hour": 0.277778, "Miles/hour": 0.44704,
                "Feet/second": 0.3048, "Knots": 0.514444
            }
        },
        "Data": {
            "units": ["Bits", "Bytes", "Kilobytes", "Megabytes", "Gigabytes", "Terabytes"],
            "to_base": {  # Convert to bytes
                "Bits": 0.125, "Bytes": 1, "Kilobytes": 1024, "Megabytes": 1048576,
                "Gigabytes": 1073741824, "Terabytes": 1099511627776
            }
        }
    }
    
    def convert(self, value, category, from_unit, to_unit):
        """Convert value from one unit to another within a category"""
        if category not in self.CONVERSIONS:
            return value
        
        if category == "Temperature":
            return self._convert_temperature(value, from_unit, to_unit)
        
        conversions = self.CONVERSIONS[category]
        base_value = value * conversions["to_base"][from_unit]
        result = base_value / conversions["to_base"][to_unit]
        return result
    
    def _convert_temperature(self, value, from_unit, to_unit):
        """Special handling for temperature conversions"""
        # Convert to Celsius first
        if from_unit == "Celsius":
            celsius = value
        elif from_unit == "Fahrenheit":
            celsius = (value - 32) * 5/9
        else:  # Kelvin
            celsius = value - 273.15
        
        # Convert from Celsius to target
        if to_unit == "Celsius":
            return celsius
        elif to_unit == "Fahrenheit":
            return celsius * 9/5 + 32
        else:  # Kelvin
            return celsius + 273.15


class ProgrammerCalculator:
    """Handles programmer mode operations"""
    
    def __init__(self):
        self.word_size = 64  # QWORD by default
        self.signed = True
        
    def convert_base(self, value, from_base, to_base):
        """Convert number between bases (2, 8, 10, 16)"""
        try:
            # Convert to decimal
            if isinstance(value, str):
                decimal_value = int(value, from_base)
            else:
                decimal_value = int(value)
            
            # Handle word size limits
            max_val = 2 ** self.word_size
            decimal_value = decimal_value % max_val
            
            # Convert to target base
            if to_base == 2:
                return bin(decimal_value)[2:]
            elif to_base == 8:
                return oct(decimal_value)[2:]
            elif to_base == 10:
                return str(decimal_value)
            elif to_base == 16:
                return hex(decimal_value)[2:].upper()
        except:
            return "0"
    
    def bitwise_operation(self, a, b, operation):
        """Perform bitwise operations"""
        operations = {
            "AND": lambda x, y: x & y,
            "OR": lambda x, y: x | y,
            "XOR": lambda x, y: x ^ y,
            "NOT": lambda x, y: ~x,
            "<<": lambda x, y: x << y,
            ">>": lambda x, y: x >> y
        }
        
        result = operations[operation](int(a), int(b) if b else 0)
        
        # Handle word size
        max_val = 2 ** self.word_size
        return result % max_val


class WindowsCalculator(tk.Tk):
    """Main Calculator Application"""
    
    def __init__(self):
        super().__init__()
        
        self.title("Calculator")
        self.geometry("320x500")
        self.configure(bg="#f3f3f3")
        self.resizable(True, True)
        
        # Initialize engines
        self.math_engine = MathEngine()
        self.conversion_service = ConversionService()
        self.programmer_calc = ProgrammerCalculator()
        
        # State variables
        self.current_mode = CalculatorMode.STANDARD
        self.display_text = tk.StringVar(value="0")
        self.expression = ""
        self.result = None
        self.is_dark_mode = False
        self.always_on_top = False
        
        self.setup_ui()
        self.bind_keyboard_shortcuts()
        
    def setup_ui(self):
        """Setup the main user interface"""
        # Menu bar
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        # Mode menu
        mode_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="☰", menu=mode_menu)
        
        for mode in CalculatorMode:
            mode_menu.add_command(label=mode.value, 
                                 command=lambda m=mode: self.switch_mode(m))
        
        mode_menu.add_separator()
        mode_menu.add_checkbutton(label="Always on top", 
                                  command=self.toggle_always_on_top)
        mode_menu.add_checkbutton(label="Dark mode", 
                                  command=self.toggle_theme)
        
        # Display
        self.display = tk.Entry(self, textvariable=self.display_text,
                               font=("Segoe UI", 32, "bold"),
                               justify="right", bd=0, bg="white",
                               fg="#000", state="readonly")
        self.display.pack(fill=tk.BOTH, padx=5, pady=5, ipady=20)
        
        # Container for mode-specific UI
        self.mode_container = tk.Frame(self, bg="#f3f3f3")
        self.mode_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Load initial mode
        self.switch_mode(CalculatorMode.STANDARD)
    
    def switch_mode(self, mode):
        """Switch between calculator modes"""
        self.current_mode = mode
        self.expression = ""
        self.display_text.set("0")
        
        # Clear mode container
        for widget in self.mode_container.winfo_children():
            widget.destroy()
        
        # Load appropriate mode UI
        if mode == CalculatorMode.STANDARD:
            self.setup_standard_mode()
        elif mode == CalculatorMode.SCIENTIFIC:
            self.setup_scientific_mode()
        elif mode == CalculatorMode.PROGRAMMER:
            self.setup_programmer_mode()
        elif mode == CalculatorMode.DATE:
            self.setup_date_mode()
        elif mode == CalculatorMode.CONVERTER:
            self.setup_converter_mode()
        elif mode == CalculatorMode.GRAPHING:
            self.setup_graphing_mode()
    
    def setup_standard_mode(self):
        """Setup Standard Calculator UI"""
        buttons = [
            ['MC', 'MR', 'M+', 'M-', 'MS'],
            ['%', 'CE', 'C', '⌫'],
            ['1/x', 'x²', '√', '÷'],
            ['7', '8', '9', '×'],
            ['4', '5', '6', '-'],
            ['1', '2', '3', '+'],
            ['±', '0', '.', '=']
        ]
        
        for row_idx, row in enumerate(buttons):
            row_frame = tk.Frame(self.mode_container, bg="#f3f3f3")
            row_frame.pack(fill=tk.BOTH, expand=True)
            
            for btn_text in row:
                btn = tk.Button(row_frame, text=btn_text,
                              font=("Segoe UI", 14),
                              command=lambda t=btn_text: self.handle_button(t))
                
                # Style specific buttons
                if btn_text in ['=']:
                    btn.config(bg="#0078d4", fg="white", activebackground="#005a9e")
                elif btn_text in ['÷', '×', '-', '+']:
                    btn.config(bg="#f0f0f0")
                elif btn_text in ['C', 'CE', '⌫']:
                    btn.config(bg="#fef6f6")
                else:
                    btn.config(bg="white")
                
                btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2, pady=2)
    
    def setup_scientific_mode(self):
        """Setup Scientific Calculator UI"""
        func_buttons = [
            ['2nd', 'π', 'e', 'C', '⌫'],
            ['x²', '1/x', '|x|', 'exp', 'mod'],
            ['√', '(', ')', 'n!', '÷'],
            ['xʸ', '7', '8', '9', '×'],
            ['log', '4', '5', '6', '-'],
            ['ln', '1', '2', '3', '+'],
            ['sin', '±', '0', '.', '=']
        ]
        
        for row in func_buttons:
            row_frame = tk.Frame(self.mode_container, bg="#f3f3f3")
            row_frame.pack(fill=tk.BOTH, expand=True)
            
            for btn_text in row:
                btn = tk.Button(row_frame, text=btn_text,
                              font=("Segoe UI", 12),
                              command=lambda t=btn_text: self.handle_button(t))
                
                if btn_text == '=':
                    btn.config(bg="#0078d4", fg="white")
                elif btn_text in ['÷', '×', '-', '+']:
                    btn.config(bg="#f0f0f0")
                else:
                    btn.config(bg="white")
                
                btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2, pady=2)
    
    def setup_programmer_mode(self):
        """Setup Programmer Calculator UI"""
        frame = tk.Frame(self.mode_container, bg="#f3f3f3")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Base selection
        base_frame = tk.Frame(frame, bg="#f3f3f3")
        base_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.current_base = tk.StringVar(value="DEC")
        for base in ["HEX", "DEC", "OCT", "BIN"]:
            tk.Radiobutton(base_frame, text=base, variable=self.current_base,
                          value=base, font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=5)
        
        # Programmer buttons
        prog_buttons = [
            ['A', 'B', 'C', 'D', 'E', 'F'],
            ['AND', 'OR', 'XOR', 'NOT', '<<', '>>'],
            ['7', '8', '9', '÷', 'C', '⌫'],
            ['4', '5', '6', '×', '(', ')'],
            ['1', '2', '3', '-', 'CE', '='],
            ['0', '.', '+']
        ]
        
        for row in prog_buttons:
            row_frame = tk.Frame(frame, bg="#f3f3f3")
            row_frame.pack(fill=tk.BOTH, expand=True)
            
            for btn_text in row:
                btn = tk.Button(row_frame, text=btn_text,
                              font=("Segoe UI", 11),
                              command=lambda t=btn_text: self.handle_programmer_button(t))
                btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=1, pady=1)
    
    def setup_date_mode(self):
        """Setup Date Calculator UI"""
        frame = tk.Frame(self.mode_container, bg="white")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(frame, text="Date Calculation", font=("Segoe UI", 16, "bold"),
                bg="white").pack(pady=10)
        
        # Date difference calculator
        tk.Label(frame, text="Difference between dates:", 
                font=("Segoe UI", 12), bg="white").pack(anchor="w", pady=5)
        
        date_frame = tk.Frame(frame, bg="white")
        date_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(date_frame, text="From:", bg="white").grid(row=0, column=0, sticky="w")
        self.date_from = tk.Entry(date_frame, width=15)
        self.date_from.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_from.grid(row=0, column=1, padx=5)
        
        tk.Label(date_frame, text="To:", bg="white").grid(row=1, column=0, sticky="w")
        self.date_to = tk.Entry(date_frame, width=15)
        self.date_to.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_to.grid(row=1, column=1, padx=5)
        
        tk.Button(frame, text="Calculate Difference", 
                 command=self.calculate_date_difference,
                 bg="#0078d4", fg="white", font=("Segoe UI", 11)).pack(pady=10)
        
        self.date_result = tk.Label(frame, text="", font=("Segoe UI", 12),
                                   bg="white", fg="#0078d4")
        self.date_result.pack(pady=10)
    
    def setup_converter_mode(self):
        """Setup Unit Converter UI"""
        frame = tk.Frame(self.mode_container, bg="white")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(frame, text="Unit Converter", font=("Segoe UI", 16, "bold"),
                bg="white").pack(pady=10)
        
        # Category selection
        tk.Label(frame, text="Category:", font=("Segoe UI", 11), 
                bg="white").pack(anchor="w")
        self.conv_category = ttk.Combobox(frame, values=list(
            self.conversion_service.CONVERSIONS.keys()), state="readonly")
        self.conv_category.set("Length")
        self.conv_category.pack(fill=tk.X, pady=5)
        self.conv_category.bind("<<ComboboxSelected>>", self.update_converter_units)
        
        # From unit
        tk.Label(frame, text="From:", font=("Segoe UI", 11),
                bg="white").pack(anchor="w", pady=(10, 0))
        self.from_unit = ttk.Combobox(frame, state="readonly")
        self.from_unit.pack(fill=tk.X, pady=5)
        
        self.from_value = tk.Entry(frame, font=("Segoe UI", 14))
        self.from_value.insert(0, "1")
        self.from_value.pack(fill=tk.X, pady=5)
        
        # To unit
        tk.Label(frame, text="To:", font=("Segoe UI", 11),
                bg="white").pack(anchor="w", pady=(10, 0))
        self.to_unit = ttk.Combobox(frame, state="readonly")
        self.to_unit.pack(fill=tk.X, pady=5)
        
        self.to_value = tk.Label(frame, text="1", font=("Segoe UI", 18, "bold"),
                                bg="white", fg="#0078d4")
        self.to_value.pack(fill=tk.X, pady=10)
        
        tk.Button(frame, text="Convert", command=self.perform_conversion,
                 bg="#0078d4", fg="white", font=("Segoe UI", 12)).pack(pady=10)
        
        self.update_converter_units()
    
    def setup_graphing_mode(self):
        """Setup Graphing Calculator UI"""
        frame = tk.Frame(self.mode_container, bg="white")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(frame, text="Graphing Calculator", font=("Segoe UI", 16, "bold"),
                bg="white").pack(pady=10)
        
        tk.Label(frame, text="Enter equation (e.g., x**2 + 2*x + 1):",
                font=("Segoe UI", 11), bg="white").pack(anchor="w")
        
        self.graph_equation = tk.Entry(frame, font=("Segoe UI", 12))
        self.graph_equation.insert(0, "x**2")
        self.graph_equation.pack(fill=tk.X, pady=5)
        
        tk.Button(frame, text="Plot Graph", command=self.plot_graph,
                 bg="#0078d4", fg="white", font=("Segoe UI", 12)).pack(pady=10)
        
        # Canvas for graph
        self.graph_canvas = tk.Canvas(frame, bg="white", height=300)
        self.graph_canvas.pack(fill=tk.BOTH, expand=True)
    
    def handle_button(self, button_text):
        """Handle button presses in standard/scientific mode"""
        current = self.display_text.get()
        
        # Number buttons
        if button_text.isdigit():
            if current == "0" or self.result is not None:
                self.display_text.set(button_text)
                self.expression = button_text
                self.result = None
            else:
                self.display_text.set(current + button_text)
                self.expression += button_text
        
        # Decimal point
        elif button_text == '.':
            if '.' not in current:
                self.display_text.set(current + '.')
                self.expression += '.'
        
        # Operators
        elif button_text in ['+', '-', '×', '÷']:
            self.expression += f" {button_text} "
            self.display_text.set(self.expression)
            self.result = None
        
        # Special functions
        elif button_text == '√':
            try:
                val = float(current)
                result = math.sqrt(val)
                self.display_text.set(str(result))
                self.result = result
            except:
                self.display_text.set("Error")
        
        elif button_text == 'x²':
            try:
                val = float(current)
                result = val ** 2
                self.display_text.set(str(result))
                self.result = result
            except:
                self.display_text.set("Error")
        
        elif button_text == '1/x':
            try:
                val = float(current)
                result = 1 / val
                self.display_text.set(str(result))
                self.result = result
            except:
                self.display_text.set("Error")
        
        elif button_text == '±':
            try:
                val = float(current)
                self.display_text.set(str(-val))
                self.expression = str(-val)
            except:
                pass
        
        elif button_text == '%':
            try:
                val = float(current)
                result = val / 100
                self.display_text.set(str(result))
                self.result = result
            except:
                self.display_text.set("Error")
        
        # Memory operations
        elif button_text == 'MC':
            self.math_engine.clear_memory()
        elif button_text == 'MR':
            mem = self.math_engine.recall_memory()
            self.display_text.set(str(mem))
        elif button_text == 'M+':
            self.math_engine.add_to_memory(float(current))
        elif button_text == 'M-':
            self.math_engine.subtract_from_memory(float(current))
        elif button_text == 'MS':
            self.math_engine.store_memory(float(current))
        
        # Scientific functions
        elif button_text in ['sin', 'cos', 'tan', 'ln', 'log']:
            try:
                val = float(current)
                if button_text == 'sin':
                    result = math.sin(math.radians(val))
                elif button_text == 'cos':
                    result = math.cos(math.radians(val))
                elif button_text == 'tan':
                    result = math.tan(math.radians(val))
                elif button_text == 'ln':
                    result = math.log(val)
                elif button_text == 'log':
                    result = math.log10(val)
                self.display_text.set(str(result))
                self.result = result
            except:
                self.display_text.set("Error")
        
        elif button_text == 'π':
            self.display_text.set(str(math.pi))
            self.expression = str(math.pi)
        
        elif button_text == 'e':
            self.display_text.set(str(math.e))
            self.expression = str(math.e)
        
        elif button_text == 'n!':
            try:
                val = int(float(current))
                result = math.factorial(val)
                self.display_text.set(str(result))
                self.result = result
            except:
                self.display_text.set("Error")
        
        # Clear operations
        elif button_text == 'C':
            self.display_text.set("0")
            self.expression = ""
            self.result = None
        
        elif button_text == 'CE':
            self.display_text.set("0")
        
        elif button_text == '⌫':
            if len(current) > 1:
                self.display_text.set(current[:-1])
                self.expression = self.expression[:-1]
            else:
                self.display_text.set("0")
                self.expression = ""
        
        # Equals
        elif button_text == '=':
            try:
                result = self.math_engine.evaluate(self.expression)
                self.display_text.set(str(result))
                self.math_engine.history.append(f"{self.expression} = {result}")
                self.result = result
                self.expression = str(result)
            except Exception as e:
                self.display_text.set("Error")
    
    def handle_programmer_button(self, button_text):
        """Handle programmer mode buttons"""
        current_base = self.current_base.get()
        base_map = {"HEX": 16, "DEC": 10, "OCT": 8, "BIN": 2}
        
        current = self.display_text.get()
        
        if button_text in '0123456789ABCDEF':
            if current == "0":
                self.display_text.set(button_text)
            else:
                self.display_text.set(current + button_text)
        
        elif button_text in ['AND', 'OR', 'XOR', 'NOT', '<<', '>>']:
            # Store operation for next calculation
            self.prog_operation = button_text
            self.prog_first_operand = int(current, base_map[current_base])
            self.display_text.set("0")
        
        elif button_text == '=':
            if hasattr(self, 'prog_operation'):
                second = int(current, base_map[current_base])
                result = self.programmer_calc.bitwise_operation(
                    self.prog_first_operand, second, self.prog_operation
                )
                # Convert back to current base
                converted = self.programmer_calc.convert_base(
                    result, 10, base_map[current_base]
                )
                self.display_text.set(converted)
        
        elif button_text == 'C':
            self.display_text.set("0")
    
    def calculate_date_difference(self):
        """Calculate difference between two dates"""
        try:
            date1 = datetime.strptime(self.date_from.get(), "%Y-%m-%d")
            date2 = datetime.strptime(self.date_to.get(), "%Y-%m-%d")
            
            diff = abs((date2 - date1).days)
            years = diff // 365
            months = (diff % 365) // 30
            days = (diff % 365) % 30
            
            result = f"{years} years, {months} months, {days} days\n({diff} total days)"
            self.date_result.config(text=result)
        except Exception as e:
            self.date_result.config(text=f"Error: {str(e)}")
    
    def update_converter_units(self, event=None):
        """Update unit dropdowns based on selected category"""
        category = self.conv_category.get()
        units = self.conversion_service.CONVERSIONS[category]["units"]
        
        self.from_unit.config(values=units)
        self.to_unit.config(values=units)
        
        self.from_unit.set(units[0])
        self.to_unit.set(units[1] if len(units) > 1 else units[0])
    
    def perform_conversion(self):
        """Perform unit conversion"""
        try:
            value = float(self.from_value.get())
            category = self.conv_category.get()
            from_u = self.from_unit.get()
            to_u = self.to_unit.get()
            
            result = self.conversion_service.convert(value, category, from_u, to_u)
            self.to_value.config(text=f"{result:.6f}")
        except Exception as e:
            self.to_value.config(text="Error")
    
    def plot_graph(self):
        """Plot graph of the equation"""
        try:
            equation = self.graph_equation.get()
            
            # Clear canvas
            self.graph_canvas.delete("all")
            
            # Get canvas dimensions
            width = self.graph_canvas.winfo_width()
            height = self.graph_canvas.winfo_height()
            
            if width < 2 or height < 2:
                width, height = 400, 300
            
            # Draw axes
            center_x = width // 2
            center_y = height // 2
            
            self.graph_canvas.create_line(0, center_y, width, center_y, 
                                         fill="gray", width=2)  # X-axis
            self.graph_canvas.create_line(center_x, 0, center_x, height, 
                                         fill="gray", width=2)  # Y-axis
            
            # Scale for graph
            scale_x = 20  # pixels per unit
            scale_y = 20
            
            # Plot equation
            points = []
            x_range = width / scale_x
            
            for pixel_x in range(width):
                x = (pixel_x - center_x) / scale_x
                try:
                    # Evaluate equation
                    y = eval(equation, {"__builtins__": {}}, 
                           {"x": x, "sin": math.sin, "cos": math.cos, 
                            "tan": math.tan, "sqrt": math.sqrt, "exp": math.exp,
                            "log": math.log, "abs": abs, "pi": math.pi, "e": math.e})
                    
                    # Convert to canvas coordinates
                    pixel_y = center_y - (y * scale_y)
                    
                    # Only plot if within canvas bounds
                    if 0 <= pixel_y <= height:
                        points.append((pixel_x, pixel_y))
                except:
                    continue
            
            # Draw the curve
            if len(points) > 1:
                for i in range(len(points) - 1):
                    self.graph_canvas.create_line(points[i][0], points[i][1],
                                                 points[i+1][0], points[i+1][1],
                                                 fill="#0078d4", width=2)
            
            # Add grid lines
            for i in range(-10, 11):
                if i != 0:
                    x_pos = center_x + (i * scale_x)
                    y_pos = center_y + (i * scale_y)
                    
                    if 0 <= x_pos <= width:
                        self.graph_canvas.create_line(x_pos, 0, x_pos, height,
                                                     fill="#e0e0e0", width=1)
                    if 0 <= y_pos <= height:
                        self.graph_canvas.create_line(0, y_pos, width, y_pos,
                                                     fill="#e0e0e0", width=1)
            
        except Exception as e:
            self.graph_canvas.delete("all")
            self.graph_canvas.create_text(200, 150, 
                                         text=f"Error plotting: {str(e)}",
                                         fill="red", font=("Segoe UI", 12))
    
    def toggle_always_on_top(self):
        """Toggle always on top window attribute"""
        self.always_on_top = not self.always_on_top
        self.attributes("-topmost", self.always_on_top)
    
    def toggle_theme(self):
        """Toggle between dark and light themes"""
        self.is_dark_mode = not self.is_dark_mode
        
        if self.is_dark_mode:
            bg_color = "#202020"
            fg_color = "#ffffff"
            display_bg = "#2d2d2d"
            button_bg = "#333333"
        else:
            bg_color = "#f3f3f3"
            fg_color = "#000000"
            display_bg = "white"
            button_bg = "white"
        
        self.configure(bg=bg_color)
        self.display.config(bg=display_bg, fg=fg_color)
        self.mode_container.config(bg=bg_color)
        
        # Update all child widgets
        for widget in self.mode_container.winfo_children():
            self._update_widget_theme(widget, bg_color, fg_color, button_bg)
    
    def _update_widget_theme(self, widget, bg, fg, button_bg):
        """Recursively update widget themes"""
        try:
            if isinstance(widget, tk.Button):
                if widget['bg'] not in ['#0078d4', '#fef6f6']:
                    widget.config(bg=button_bg, fg=fg)
            elif isinstance(widget, (tk.Frame, tk.Label)):
                widget.config(bg=bg, fg=fg)
            
            for child in widget.winfo_children():
                self._update_widget_theme(child, bg, fg, button_bg)
        except:
            pass
    
    def bind_keyboard_shortcuts(self):
        """Bind keyboard shortcuts"""
        self.bind('<Return>', lambda e: self.handle_button('='))
        self.bind('<BackSpace>', lambda e: self.handle_button('⌫'))
        self.bind('<Escape>', lambda e: self.handle_button('C'))
        
        # Number keys
        for i in range(10):
            self.bind(str(i), lambda e, n=str(i): self.handle_button(n))
        
        # Operator keys
        self.bind('+', lambda e: self.handle_button('+'))
        self.bind('-', lambda e: self.handle_button('-'))
        self.bind('*', lambda e: self.handle_button('×'))
        self.bind('/', lambda e: self.handle_button('÷'))
        self.bind('.', lambda e: self.handle_button('.'))
        self.bind('%', lambda e: self.handle_button('%'))


# Additional Features and Services

class CurrencyService:
    """Mock currency conversion service"""
    
    # Mock exchange rates (USD as base)
    RATES = {
        "USD": 1.0,
        "EUR": 0.85,
        "GBP": 0.73,
        "JPY": 110.0,
        "CNY": 6.45,
        "INR": 74.5,
        "AUD": 1.35,
        "CAD": 1.25,
        "CHF": 0.92,
        "MXN": 20.0
    }
    
    def convert(self, amount, from_currency, to_currency):
        """Convert between currencies using mock rates"""
        if from_currency not in self.RATES or to_currency not in self.RATES:
            return amount
        
        # Convert to USD first, then to target currency
        usd_amount = amount / self.RATES[from_currency]
        result = usd_amount * self.RATES[to_currency]
        return result
    
    def get_currencies(self):
        """Get list of available currencies"""
        return list(self.RATES.keys())


class HistoryManager:
    """Manage calculation history"""
    
    def __init__(self, max_items=50):
        self.history = []
        self.max_items = max_items
    
    def add(self, expression, result):
        """Add calculation to history"""
        entry = {
            "expression": expression,
            "result": result,
            "timestamp": datetime.now()
        }
        self.history.insert(0, entry)
        
        # Keep only max_items
        if len(self.history) > self.max_items:
            self.history = self.history[:self.max_items]
    
    def get_all(self):
        """Get all history entries"""
        return self.history
    
    def clear(self):
        """Clear all history"""
        self.history = []
    
    def search(self, query):
        """Search history for query"""
        results = []
        for entry in self.history:
            if query.lower() in entry["expression"].lower():
                results.append(entry)
        return results


class PluginSystem:
    """Extensible plugin system for custom conversions"""
    
    def __init__(self):
        self.plugins = {}
    
    def register_plugin(self, name, plugin_class):
        """Register a new conversion plugin"""
        self.plugins[name] = plugin_class()
    
    def get_plugin(self, name):
        """Get a registered plugin"""
        return self.plugins.get(name)
    
    def list_plugins(self):
        """List all registered plugins"""
        return list(self.plugins.keys())


class CustomConversionPlugin:
    """Base class for custom conversion plugins"""
    
    def __init__(self, name, units, conversions):
        self.name = name
        self.units = units
        self.conversions = conversions
    
    def convert(self, value, from_unit, to_unit):
        """Convert between units"""
        if from_unit not in self.conversions or to_unit not in self.conversions:
            return value
        
        base_value = value * self.conversions[from_unit]
        result = base_value / self.conversions[to_unit]
        return result


# Example custom plugin: Cooking measurements
class CookingPlugin(CustomConversionPlugin):
    def __init__(self):
        super().__init__(
            name="Cooking",
            units=["Teaspoons", "Tablespoons", "Cups", "Fluid Ounces", "Milliliters"],
            conversions={  # Convert to milliliters
                "Teaspoons": 4.92892,
                "Tablespoons": 14.7868,
                "Cups": 236.588,
                "Fluid Ounces": 29.5735,
                "Milliliters": 1.0
            }
        )
def main():
    """Main entry point"""
    app = WindowsCalculator()
    app.mainloop()


if __name__ == "__main__":
    main()

