from langchain_community.document_loaders import WebBaseLoader
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import ResponseSchema
from langchain.output_parsers import StructuredOutputParser
from langchain.prompts import PromptTemplate 
from langchain.chat_models import ChatOpenAI 
from langchain.chains import LLMChain
from dotenv import load_dotenv
import requests
from fastapi import FastAPI,Form
import re
import openai


load_dotenv()


app = FastAPI()

def is_shortened_url(url):                                  # It is checking whether it is a shorten url or regular website url 
    try:
        response = requests.head(url, allow_redirects=True)
        final_url = response.url
        if final_url != url:
            return True
        return False
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return False

def expand_short_url(short_url):                      # It is converting shorten url to regular url 
    try:
        response = requests.head(short_url, allow_redirects=True)
        if response.status_code == 200:
            return response.url
        else:
            print("Error: Short URL couldn't be expanded.")
            return None
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return None

def get_original_url(url):
    if is_shortened_url(url):
        return expand_short_url(url)
    else:
        return url



# This is the complete code where we are extracting content from the url using WebBaseLoader , using LLM to extract blog content only and then paraphrasing it
def paraphrased_post(url): 
    loader=WebBaseLoader([url],encoding='utf-8')
    docs = loader.load()

    template="""You are a helpful LinkedIn webscrapper. You are provided with a data , extract the content of the post only.
            {docs}"""


    prompt=PromptTemplate(template=template,input_variables=['docs'])
    llm=ChatOpenAI(temperature=0)
    chain=LLMChain(llm=llm,prompt=prompt)


    result=chain.invoke({'docs':docs},return_only_outputs=True)

    data=result['text']

    template="""You are a helpful LinkedIn post paraphraser and plagiarism remover bot. You are provided with LinkedIn post content and your task is to paraphrase it and remove plagiarism .Return the output in the format with spaces or stickers if present.
                {data}"""

    prompt2=PromptTemplate(template=template,input_variables=['data'])
    llm=ChatOpenAI(temperature=0)
    chain2=LLMChain(llm=llm,prompt=prompt2)

    result2=chain2({'data':data},return_only_outputs=True)
    data2=extract_data(result2['text'])
    keywords=data2['Keywords'][:3]
    take_aways=data2['Take Aways'][:3]
    highlights=data2['Highlights'][:3]
    return result2['text'] ,keywords , take_aways, highlights


def extract_data(post_data):
    keywords = ResponseSchema(name="Keywords",
                        description="These are the keywords extracted from LinkedIn post",type="list")

    Take_aways = ResponseSchema(name="Take Aways",
                                description="These are the take aways extracted from LinkedIn post", type= "list")
    Highlights=ResponseSchema(name="Highlights",
                                description="These are the highlights extracted from LinkedIn post", type= "list")

    response_schema = [
        keywords,
        Take_aways,
        Highlights

    ]
    output_parser = StructuredOutputParser.from_response_schemas(response_schema)
    format_instructions = output_parser.get_format_instructions()

    template = """
        You are a helpful keywords , take aways and highlights extractor from the post of LinkedIn Bot. Your task is to extract relevant keywords , take aways and highlights extractor.
        From the following text message, extract the following information:

        text message: {content}
        {format_instructions}
        """
    
    prompt_template = ChatPromptTemplate.from_template(template)
    messages = prompt_template.format_messages(content=post_data, format_instructions=format_instructions)
    llm = ChatOpenAI(temperature=0)
    response = llm(messages)
    output_dict=  output_parser.parse(response.content)
    return  output_dict




# Define a route to handle POST requests to '/paraphrase'

@app.post("/paraphrase")
async def paraphrase(url: str = Form(...)):
    try:
        if url:
            original_url=get_original_url(url)
            match = re.match(r"https?://(?:www\.)?linkedin\.com/(posts|feed|pulse)/.*", original_url)  # checking domain and url page (means it should only be a post nothing else like login page or something else)

            if match :
                paraphrased_content,keywords, take_aways , highlights =paraphrased_post(original_url)
                return {"Paraphrased post":paraphrased_content , "Keywords": keywords,"Take Aways":take_aways, "Highlights":highlights}
            else:
                return "Put a valid LinkedIn post url only"
        else:
            return "Please enter a link"
    except (openai.BadRequestError,TypeError) as e:
        return "Put a valid LinkedIn post url only"



