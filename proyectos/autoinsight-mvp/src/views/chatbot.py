import streamlit as st
import pandas as pd
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_groq import ChatGroq

def render_chatbot(df):
    """
    Renderiza la vista del Asesor Chatbot con un enfoque corporativo y ultraminimalista.
    """
    # --- 1. ENCABEZADO Y CONTROLES DE UI ---
    col1, col2 = st.columns([4, 1])
        
    with col2:
        if st.button("Reiniciar chat", type="primary", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
            
    # Línea separadora sutil (espacio en blanco)
    st.markdown("<div style='margin: 10px 0 30px 0;'></div>", unsafe_allow_html=True)

    # --- 2. LÓGICA DEL AGENTE ---
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except KeyError:
        st.error("Error: Falta configurar GROQ_API_KEY en st.secrets.")
        return

    if "messages" not in st.session_state or len(st.session_state.messages) == 0:
        st.session_state.messages = [
            {
                "role": "assistant", 
                "content": "Hola. Soy el asistente de **AutoInsight**.\n\nEstoy conectado al **catálogo en tiempo real**. Puedes pedirme **recomendaciones según tu presupuesto**, **filtrar por año**, o **buscar marcas específicas**.\n\n¿Qué tipo de vehículo buscas hoy?"
            }
        ]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ej: Muéstrame los vehículos marca Toyota..."):
        
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Procesando consulta..."):
                try:
                    @st.cache_resource(show_spinner=False)
                    def get_fast_agent(_df, _api_key):
                        llm = ChatGroq(
                            temperature=0, 
                            groq_api_key=_api_key, 
                            model_name="llama-3.3-70b-versatile"
                        )
                        return create_pandas_dataframe_agent(
                            llm, 
                            _df, 
                            verbose=False, 
                            allow_dangerous_code=True,
                            agent_type="zero-shot-react-description",
                            max_iterations=15,
                            handle_parsing_errors=True
                        )
                    
                    agent = get_fast_agent(df, api_key)
                    
                    instruccion = (
                        "You MUST use English for your Thought and Action steps. "
                        "Your 'Final Answer' MUST be in Spanish, professional, highly concise, and minimalist. "
                        "Do absolutely NOT use any emojis. "
                        "CRITICAL: Do NOT use the '$' symbol for currency. Whenever you provide prices, ALWAYS format them as 'CLP 10.500.000' with thousands separators to avoid markdown math formatting errors. "
                        "If asked for 'calidad-precio' or 'value for money', NEVER output raw mathematical ratios or calculated decimals (like 0.0034). Explain the value conceptually (e.g., 'low mileage for its year and price'). "
                        "Also, always include a brief, logical justification for your answer or recommendation. "
                        "User query: "
                    )
                    response = agent.invoke(instruccion + prompt)
                    respuesta_texto = response.get("output") if isinstance(response, dict) else response
                    
                    # Escapar signos de dolar para evitar que Streamlit los renderice como LaTeX (texto verde)
                    respuesta_texto = respuesta_texto.replace("$", r"\$")
                    
                    st.markdown(respuesta_texto)
                    st.session_state.messages.append({"role": "assistant", "content": respuesta_texto})
                    
                except Exception as e:
                    error_msg = str(e)
                    if "429" in error_msg or "Rate limit" in error_msg:
                        st.error("Límite de consultas alcanzado. Por favor, intenta de nuevo en un minuto.")
                        if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
                            st.session_state.messages.pop() 
                    elif "iteration limit" in error_msg.lower():
                        st.error("El asistente no pudo procesar la solicitud en el tiempo límite. Intenta reformular tu pregunta.")
                        if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
                            st.session_state.messages.pop()
                    else:
                        st.error(f"Error interno: {e}")