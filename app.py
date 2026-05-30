from flask import Flask, request, jsonify, render_template
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor

app = Flask(__name__)

def limpiar_sintaxis(expr_str):
    """Ajusta la entrada del usuario para que el motor de Python la entienda."""
    # Reemplaza el 'sen' en español por 'sin' que usa Python de forma nativa
    expr_str = expr_str.replace('sen', 'sin')
    # Reemplaza el símbolo de raíz si se llega a usar
    expr_str = expr_str.replace('√', 'sqrt')
    # Convierte el símbolo ^ en ** (potencia en Python) por seguridad
    expr_str = expr_str.replace('^', '**')
    return expr_str

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/derivar', methods=['POST'])
def derivar_funcion():
    data = request.get_json()
    
    if not data or 'funcion' not in data:
        return jsonify({'status': 'error', 'mensaje': 'No se recibió ninguna función.'}), 400
        
    entrada_usuario = data['funcion'].strip()
    entrada_limpia = limpiar_sintaxis(entrada_usuario)
    
    try:
        # Definimos 'x' como la variable simbólica principal
        x = sp.Symbol('x')
        
        # Transformaciones automáticas para entender multiplicaciones implícitas (ej: 2x -> 2*x)
        transformaciones = standard_transformations + (implicit_multiplication_application, convert_xor)
        
        # Parsea la string de texto a una expresión matemática real de SymPy
        expresion = parse_expr(entrada_limpia, transformations=transformaciones)
        
        # 1. CÁLCULO: Aplicamos la derivada respecto a x
        derivada_cruda = sp.diff(expresion, x)
        
        # 2. ÁLGEBRA ESTILO CUADERNO: Solo factorizamos términos comunes, sin alterar las funciones trigonométricas
        derivada_factorizada = sp.factor(derivada_cruda)
        
        # Convertimos los resultados a LaTeX
        latex_original = sp.latex(expresion)
        latex_resultado = sp.latex(derivada_factorizada)
        
        # Volvemos a formatear el LaTeX final para que muestre '\operatorname{sen}' en vez de '\sin'
        latex_original = latex_original.replace(r'\sin', r'\operatorname{sen}')
        latex_resultado = latex_resultado.replace(r'\sin', r'\operatorname{sen}')
        
        return jsonify({
            'status': 'success',
            'original_latex': latex_original,
            'derivada_latex': latex_resultado,
            'mensaje': 'Derivada calculada y factorizada con éxito matemático absoluto.'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'mensaje': f'Error de sintaxis matemática: {str(e)}'
        }), 400

if __name__ == '__main__':
    # El servidor se ejecutará localmente en el puerto 5000
    print(">>> Servidor de Cálculo Avanzado Activo en http://localhost:5000 <<<")
    app.run(debug=True, port=5000)