from typing import Callable

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms import HuggingFaceHub

import nbformat
import shutil

from nbformat.v4 import new_notebook, new_code_cell, new_markdown_cell

import pandas as pd
import numpy as np
# On lit nos variables environnments avec nos clés APIs
import os
from dotenv import load_dotenv, find_dotenv

import re

_ = load_dotenv(find_dotenv())

class JupyCoder():
    def __init__(self, 
                 path: str,
                 llm: Callable) -> None:
        self.llm =  llm
        self.path = path
    

    def chain_router(self, 
                     query:str) -> str:
        prompt_router =  """[[INST] Return only the name of the function to choose based on the query.
        The user have to explicitely ask to update in order to use update_last_cell or update_cell, otherwise, always create a new cell.
        The user have to explicitely ask for a markddown to use create_markdown, otherwise, use create_code_cell.
        Does not add explanation. Limit yourself to just the name of the query.
        
        Here are your options:
        Function list: 
        - create_code_cell: Create a code cell with new code lines
        - create_markdown: Create a markdown cell with new text (explanation, context)
        - update_last_cell: Update the last cell of the notebook
        - update_cell: Update the cell at the index i
        - delete_last_cell: Delete the last cell
        - delete_cell : Delete the cell at the index i
        - explain_last_cell: Explain the last cell

        "QUERY": 
        {query}
        
        Limit to one word.
        [/INST] 

        Name of the function to choose:
        """
        prompt_router_templ = PromptTemplate(input_variables=["query"], template=prompt_router)
        chain_router = LLMChain(prompt=prompt_router_templ, llm=self.llm)
        answer = chain_router.invoke({"query": query})
        return answer["text"].split("choose:")[1].strip().replace('\_', '_')
    
    def code_generation(self, 
                        query:str) -> str:
        prompt_coder =  """[INST]Generate only the python code lines to realize: {query}.
         
        Do not use a list.
        Always add extra text as commentary.

        Limit the answer to the code lines. 
        [/INST] 

        The python code is:"""
        prompt_coder_templ = PromptTemplate(input_variables=["query"], template=prompt_coder)
        chain_coder = LLMChain(prompt=prompt_coder_templ, llm=self.llm)
        answer = chain_coder.invoke({"query": query})
        return answer["text"].split("is:")[1].strip()
    
    def markdown_generation(self,
                            query:str) -> str:
        prompt_markdown =  """[INST]Ta tâche est de créer un document markdown.
        {query}.
        Sois bref. Limites toi à un paragraphe.
        [/INST] 

        Markdown:"""
        prompt_markdown_templ = PromptTemplate(input_variables=["query"], template=prompt_markdown)
        chain_markdown = LLMChain(prompt=prompt_markdown_templ, llm=self.llm)
        answer = chain_markdown.invoke({"query": query})
        return answer["text"].split("Markdown:")[1].strip()
    

    def code_explanation(self,
                         code:str) -> str:
            prompt_explanation =  """[INST]Tu dois expliquer en quelques lignes le code suivant.
            {code}.
            
            [/INST] 

            Explication:"""
            prompt_explanation_templ = PromptTemplate(input_variables=["query"], template=prompt_explanation)
            chain_explanation = LLMChain(prompt=prompt_explanation_templ, llm=self.llm)
            answer = chain_explanation.invoke({"code": code})
            return answer["text"].split("Explication:")[1].strip()


    def code_update(self, 
                    query: str, 
                    code:str) -> str:
            prompt_explanation =  """[INST]Update the code to respect the following query : {query}.
            Do not add additional text.
            Do not explain the arguments of the code and do not explain the change lines. Do not use a list.
            Remove all the sentences which are not code lines.
            
            {code}
            
            [/INST] 

            Updated Code:"""
            prompt_explanation_templ = PromptTemplate(input_variables=["query", "code"], template=prompt_explanation)
            chain_explanation = LLMChain(prompt=prompt_explanation_templ, llm=self.llm)
            answer = chain_explanation.invoke({"query": query, "code": code})
            return answer["text"].split("Code:")[1].strip()
    
    def create_notebook(self, 
                        nb_path):
        
        notebook = new_notebook()
        with open(nb_path, 'w') as f:
            nbformat.write(notebook, f)

    def load_notebook(self,
                      nb_path):
        with open(nb_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        #save the version as a backup
        #check that the folder exists
        if not os.path.exists('backup'):
            os.makedirs('backup')
        #get the name of the notebook
        notebook_name = os.path.basename(nb_path)
        #construct the backup path
        backup_path = os.path.join("backup", notebook_name)
        #copy in the backup folder
        shutil.copyfile(nb_path, backup_path)
        return nb
    
    def save_notebook(self,
                      nb_path, 
                      nb):    
        with open(nb_path, 'w', encoding='utf-8') as f:
            nbformat.write(nb, f)
            
        
    def create_code_cell(self,
                         nb_path, 
                         content):
        #load notebook
        nb = self.load_notebook(nb_path)   
        #create a new cell
        new_cell = new_code_cell(content)
        #append the cell to the notebook
        nb.cells.append(new_cell)
        #save the notebook
        self.save_notebook(nb_path, nb)
        
    def create_markdown(self,
                        nb_path, 
                        content):

        #load notebook
        nb = self.load_notebook(nb_path)
        #create a new cell
        new_cell = new_markdown_cell(content)
        #append the cell to the notebook
        nb.cells.append(new_cell)
        #save the notebook
        self.save_notebook(nb_path, nb)

    def update_last_cell(self,nb_path, content):
        #load notebook
        nb = self.load_notebook(nb_path)
        #get the cell
        cell_id = len(nb.cells)-1
        cell = nb.cells[cell_id]
        #update the cell
        cell.source = content
        #save the notebook
        self.save_notebook(nb_path, nb)

    def update_cell(self,nb_path, content, cell_id):
        #load notebook
        nb = self.load_notebook(nb_path)
        if cell_id < len(nb.cells):
            #get the cell
            cell = nb.cells[cell_id-1]
            #update the cell
            cell.source = content
            #save the notebook
            self.save_notebook(nb_path, nb)
        else:
            print("L'index de cellule spécifié est invalide.")

    def update_markdown(self,nb_path, content, cell_id):
        #load notebook
        nb = self.load_notebook(nb_path)
        if cell_id > 0 and cell_id <= len(nb.cells):
            #get the cell
            cell = nb.cells[cell_id-1]
            #check the cell type
            if cell.cell_type == "markdown":
                #update the cell
                cell.source = content
            else:
                print(f"Modification impossible car la cellule {cell_id} est une celle de markdown.")
            #save the notebook
            self.save_notebook(nb_path, nb)
        else:
            print("L'index de cellule spécifié est invalide.")

    def delete_last_cell(self,nb_path):
        #load notebook
        nb = self.load_notebook(nb_path)
        #get the cell
        cell_id = len(nb.cells)-1
        del nb.cells[cell_id]
        #save the notebook
        self.save_notebook(nb_path, nb)

    def delete_cell(self,nb_path, cell_id):
        #load notebook
        nb = self.load_notebook(nb_path)
        
        if cell_id > 0 and cell_id <= len(nb.cells):
            #delete the cell
            del nb.cells[cell_id-1]
            #save the notebook
            self.save_notebook(nb_path, nb)
        else:
            print("L'index de cellule spécifié est invalide.")

    def get_last_cell(self,
                      nb_path):
        #load notebook
        nb = self.load_notebook(nb_path)
        #get last cell
        last_cell = nb.cells[len(nb.cells)-1]
        return last_cell.source
    

    def tools(self,
              router_action, 
              query, 
              path):
        print(router_action)
        path = path.replace('\\', '/')
        if "create_code_cell" in router_action:
            code=self.code_generation(query)
            code = code.replace('\_', '_').replace('`',"")
            pattern =r'[=-]{2,}'
            clean_code = re.sub(pattern, '', code)
            pattern =r' {2,}'
            clean_code = re.sub(pattern, '', clean_code)
            pattern = '&#x200B;'
            clean_code = re.sub(pattern, '', clean_code)
            clean_code = clean_code.split("This code")[0].strip()
            self.create_code_cell(path, clean_code)
        elif "create_markdown" in router_action:
            text = self.markdown_generation(query)
            pattern =r' {2,}'
            clean_text = re.sub(pattern, '', text)
            self.create_markdown(path, clean_text)
        elif "update_last_cell" in router_action:
            code = self.get_last_cell(path) 
            print(code)
            upd_code = self.code_update(query, code)
            upd_code = upd_code.replace('\_', '_').replace('`',"")
            pattern =r'[=-]{2,}'
            clean_code = re.sub(pattern, '', upd_code)
            pattern =r' {2,}'
            clean_code = re.sub(pattern, '', clean_code)
            self.update_last_cell(path, clean_code.strip())

        elif "update_cell" in router_action:
            code = 'print("Bonjour, je viens en paix!")'
            self.create_code_cell(path, code)
        elif "update_markdown" in router_action:
            text = 'Ce code est bon, zooouh!'
            self.update_markdown(path, text)        
        elif  "delete_last_cell" in router_action:
            self.delete_last_cell(path)
        elif "delete_cell" in router_action:
            self.delete_cell(path)
        elif "explain_last_cell" in router_action:
            code = self.get_last_cell(path)
            explication = self.code_explanation(code)
            pattern =r' {2,}'
            clean_text = re.sub(pattern, '', explication)
            self.create_markdown(path, clean_text)
    
    def make_action(self, query) -> None:
        action = self.chain_router(query)
        self.tools(action, query, self.path)
