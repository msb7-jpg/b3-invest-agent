from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from statusinvest_sdk.config import OPENAI_API_KEY, OPENAI_API_BASE, OPENAI_MODEL_NAME
from statusinvest_sdk.logger import logger
import warnings
# Suprime avisos do langchain
warnings.filterwarnings("ignore")

class SentimentAnalysis(BaseModel):
    explicacao: str = Field(description="Explicação detalhada e completa sobre o documento. Deve obrigatoriamente incluir e explicar o contexto, o foco principal e os impactos (se existirem), em parágrafos bem redigidos.")
    sentimento: str = Field(description="Classificação do sentimento.", enum=["Positivo", "Neutro", "Negativo"])

class AIAnalyzer:
    """Analisador IA usando LangChain e um modelo compatível com OpenAI rodando localmente."""
    
    def __init__(self, base_url: str = None, model_name: str = None):
        # Usa DI ou variáveis de ambiente como fallback
        base_url = base_url or OPENAI_API_BASE
        model_name = model_name or OPENAI_MODEL_NAME or "local-model"
        
        # É importante o /v1 se for LM Studio, mas se o usuário definiu localhost:8080, usamos da env.
        if not base_url.endswith("/v1") and "localhost" in base_url:
            base_url = f"{base_url.rstrip('/')}/v1"
            
        logger.info(f"Inicializando Analisador IA no endpoint: {base_url} (Modelo: {model_name})")
        
        self.llm = ChatOpenAI(
            model=model_name,
            api_key=OPENAI_API_KEY or "not-needed",
            base_url=base_url,
            temperature=0.3, # Um pouco de criatividade para deixar o texto mais humano
            max_retries=2
        )
        
        # Cria um LLM com output estruturado usando Pydantic
        self.structured_llm = self.llm.with_structured_output(SentimentAnalysis)
        
        self.prompt = PromptTemplate(
            input_variables=["ticker", "categoria", "conteudo"],
            template=(
                "Você é um consultor financeiro comunicando-se diretamente com um investidor no Telegram.\n"
                "Leia o documento oficial da CVM/B3 ou atualização de mercado abaixo referente ao ativo {ticker} (Categoria: {categoria}).\n\n"
                "CONTEÚDO:\n"
                "{conteudo}\n\n"
                "Sua tarefa:\n"
                "1. Escreva uma explicação detalhada e fluida sobre o documento. Em vez de apenas frases curtas, explique corretamente tudo o que o documento aborda.\n"
                "Siga obrigatoriamente as seguintes diretrizes e estrutura no texto:\n"
                "   - Contexto (breve introdução do evento)\n"
                "   - Foco Principal (detalhes importantes, números, decisões)\n"
                "   - Impactos (caso existam, como afeta o ativo e o investidor)\n"
                "2. Classifique o sentimento geral (Positivo, Neutro ou Negativo)."
            )
        )

    def analyze_document(self, ticker: str, categoria: str, conteudo: str) -> SentimentAnalysis:
        """Envia o conteúdo do documento para o LLM local sumarizar e classificar."""
        try:
            prompt_str = self.prompt.format(ticker=ticker, categoria=categoria, conteudo=conteudo[:25000]) # Limitando a 25000 chars por segurança
            logger.info(f"Analisando documento via LLM para o ativo {ticker}...")
            
            result = self.structured_llm.invoke(prompt_str)
            return result
        except Exception as e:
            logger.error(f"Erro na análise de IA para {ticker}: {e}")
            return SentimentAnalysis(explicacao=f"Falha ao gerar explicação pela IA: {e}", sentimento="Neutro")
