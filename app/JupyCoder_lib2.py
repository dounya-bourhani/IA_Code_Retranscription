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
        prompt_router =  """[[INST] Identifie l'action à réaliser en fonction de "QUERY" puis donnes le nom de la fonction à choisir.
        L'utilisateur doit explicitement demander une mise à jour pour utiliser update_last_cell ou update_cell, sinon, il faut toujours créer une nouvelle cellule.
        L'utilisateur doit demander explicitement un markdown pour utiliser une cellule en relation avec les markdowns.
        Si l'utilisateur précise une cellule avec une clé JupyCoder, utilises update_selected_cell, update_selected_markdown ou delete_selected_cell.
        N'ajoute pas d'explication. Se limiter au nom de la requête.
        Si l'utilisateur, précise qu'il fait référence à la dernière cellule, prends les fonctions correspondantes: update_last_cell, update_last_markdown, delete_last_cell ou explain_last_cell.
        
        Voici les fonctions disponibles pour créer une cellule :
        - create_code_cell : Créer une cellule de code avec de nouvelles lignes de code
        - create_markdown : Créer une cellule markdown avec du nouveau texte (explication, contexte)
        
        Voici les fonctions disponibles pour modifier une cellule: 
        - update_last_cell : Mise à jour de la dernière cellule du carnet
        - update_last_markdown : Mise à jour de la dernière cellule markdown
        - update_selected_cell : Met à jour de la cellule de code qui a la clé JupyCoder
        - update_selected_markdown : Met à jour du markdown qui a la clé JupyCoder
        
        Voici les fonctions disponibles pour supprimer une cellule:
        - delete_last_cell : Supprime la dernière cellule
        - delete_selected_cell : Supprime la cellule qui a la clé JupyCoder

        Voici les fonctions pour expliquer une cellule:
        - explain_last_cell : Explique la dernière cellule
        - explain_selected_cell : Explique la cellule qui a la clé JupyCoder

        Voici les fonctions pour résumer le notebook.
        - summary_all : Créer un résumé de tous le notebook
        
        "QUERY": 
        {query}

        Limites toi à une fonction. 
        [/INST] 
        
        Nom de la fonction à choisir:
        """
        prompt_router_templ = PromptTemplate(input_variables=["query"], template=prompt_router)
        chain_router = LLMChain(prompt=prompt_router_templ, llm=self.llm)
        answer = chain_router.invoke({"query": query})
        return answer["text"].split("choisir:")[1].strip().replace('\_', '_')
    
    def code_generation(self, 
                        query:str,
                        history) -> str:
        ### Si besoin, ajouter ``` python ``` au lieu de mon code python est:
        prompt_coder =  """[INST]Génères uniquement les lignes de code python pour réaliser la requête suivante : {query}. 
        Voici l'historique des dernières commandes, si besoin, sers en toi pour améliorer le code: 
        {history}

        Ajoutes du texte supplémentaire comme commentaire si besoin. 
        Limite ta réponse à des lignes de code.
        [/INST] 

        Le code python est:"""
        prompt_coder_templ = PromptTemplate(input_variables=["query", "history"], template=prompt_coder)
        chain_coder = LLMChain(prompt=prompt_coder_templ, llm=self.llm)
        answer = chain_coder.invoke({"query": query, "history": history})
        response = answer["text"].split("est:")[1].strip()
        if 'Explanation' in response:
            response = response.split("Explanation:")[0].strip()
        elif 'Notes' in response:
            response = response.split("Notes:")[0].strip()
        return response
    
    
    def markdown_generation(self,
                            query:str) -> str:
        prompt_markdown =  """[INST]Ta tâche est de créer un document markdown.
        {query}.
        Sois bref. Limites toi à un paragraphe. N'ajoutes pas d'onglet Explication.
        [/INST] 

        Markdown:"""
        prompt_markdown_templ = PromptTemplate(input_variables=["query"], template=prompt_markdown)
        chain_markdown = LLMChain(prompt=prompt_markdown_templ, llm=self.llm)
        answer = chain_markdown.invoke({"query": query})
        return answer["text"].split("Markdown:")[1].strip()
    
    def markdown_update(self,
                            text: str,
                            query:str) -> str:
        prompt_markdown_upd =  """[INST]{query}.
        
        Markdown: 
        {markdown}

        Sois bref. Limites toi à un paragraphe.
        [/INST] 

        Markdown modifié:"""
        prompt_markdown__updtempl = PromptTemplate(input_variables=["query", "markdown"], template=prompt_markdown_upd)
        chain_markdown = LLMChain(prompt=prompt_markdown__updtempl, llm=self.llm)
        answer = chain_markdown.invoke({"query": query, "markdown":text})
        return answer["text"].split("modifié:")[1].strip()    

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
            Do not add additional text or explanation. Add commentaries if necessary.
            Do not explain the arguments of the code and do not explain the change lines. Do not use a list.
            Remove all the sentences which are not code lines.
            
            {code}
            
            Limit yourself to the code lines. 
            [/INST] 

            Updated Code:"""
            prompt_explanation_templ = PromptTemplate(input_variables=["query", "code"], template=prompt_explanation)
            chain_explanation = LLMChain(prompt=prompt_explanation_templ, llm=self.llm)
            answer = chain_explanation.invoke({"query": query, "code": code})
            return answer["text"].split("Code:")[1].strip()
    
    def chain_query_augmentation(self, 
                                 query: str) -> str:
            prompt_augmentation =  """[INST]Ta tâche est d'améliorer la requête utilisateur en la réécrivant \
            pour qu'elle soit mieux comprise pour de la génération de code python. \
            Apportes toutes les informations nécessaires qui pourrait aider à générer du code python en relation avec: {query}. 

            Limites toi à une phrase.
            [/INST] 

            Requête améliorée:"""
            prompt_augmentation_templ = PromptTemplate(input_variables=["query"], template=prompt_augmentation)
            chain_augmentation = LLMChain(prompt=prompt_augmentation_templ, llm=self.llm)
            answer = chain_augmentation.invoke({"query": query})
            return answer["text"].split("améliorée:")[1].strip()

    def chain_summary(self, 
                      list_codes):
            prompt_summary =  """[INST]Ton rôle est de résumer  en language naturel les commandes python réalisée dans ce notebook:
            {codes}

            Limite toi à un paragraphe. 
            [/INST] 

            Réponse:
            Dans ce notebook,"""
            prompt_summary_templ = PromptTemplate(input_variables=["codes"], template=prompt_summary)
            chain_summary = LLMChain(prompt=prompt_summary_templ, llm=self.llm)
            answer = chain_summary.invoke({"codes": list_codes})
            return answer["text"].split("Réponse:")[1].strip()                


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
        if cell_id[0] < len(nb.cells):
            #get the cell
            cell = nb.cells[cell_id[0]]
            print(cell)
            #update the cell
            cell.source = content
            #save the notebook
            print(cell)
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

    def update_last_markdown(self,nb_path, content):
        #load notebook
        nb = self.load_notebook(nb_path)
        #get the cell
        cell_id = len(nb.cells)-1
        cell = nb.cells[cell_id]
        #check the cell type
        if cell.cell_type == "markdown":
            #update the cell
            cell.source = content
        else:
            print(f"Modification impossible car la cellule {cell_id} est une celle de code.")
        #save the notebook
        self.save_notebook(nb_path, nb)

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
        print(cell_id)
        
        if cell_id[0] > 0 and cell_id[0] <= len(nb.cells):
            #delete the cell
            del nb.cells[cell_id[0]]
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
    
    def get_cell_to_update(self,
                           nb_path):
        #load notebook
        nb = self.load_notebook(nb_path)
        all_codes = [cell["source"] for cell in nb.cells]
        ind_update = [ind for ind, cell in enumerate(all_codes)  if '## A MODIFIER ##' in cell]
        print(ind_update)
        code = all_codes[ind_update[0]]
        return ind_update,code 
    
    def get_cell_to_delete(self,
                           nb_path):
        #load notebook
        nb = self.load_notebook(nb_path)
        all_codes = [cell["source"] for cell in nb.cells]
        ind_delete = [ind for ind, cell in enumerate(all_codes)  if '## A SUPPRIMER ##' in cell]

        return ind_delete
    
    def get_cell_to_explain(self, 
                            nb_path):
        
        #load notebook
        nb = self.load_notebook(nb_path)
        all_codes = [cell["source"] for cell in nb.cells]
        ind_update = [ind for ind, cell in enumerate(all_codes)  if '## A EXPLIQUER ##' in cell]
        code = all_codes[ind_update[0]]
        return code 
        
    def get_all_cell(self,
                      nb_path):
        #load notebook
        nb = self.load_notebook(nb_path)
        #get last cell
        all_codes = [cell["source"] for cell in nb.cells if cell.get('cell_type') == 'code']

        return all_codes
    
    def tools(self,
              router_action, 
              query, 
              path):
        print(router_action)
        path = path.replace('\\', '/')
        if "create_code_cell" in router_action:
            list_codes = self.get_all_cell(self.path)
            history = list_codes[-5:]
            code=self.code_generation(query, history)
            code = code.replace('\_', '_').replace('`',"").replace("python", "").replace('\#', '#')
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
            pattern =r'[=-]{2,}'
            clean_text = re.sub(pattern, '', text)
            pattern =r' {2,}'
            clean_text = re.sub(pattern, '', clean_text)
            self.create_markdown(path, clean_text)
        elif "update_last_cell" in router_action:
            code = self.get_last_cell(path) 
            print(code)
            upd_code = self.code_update(query, code)
            upd_code = upd_code.replace('\_', '_').replace('`',"").replace("python", "")
            pattern =r'[=-]{2,}'
            clean_code = re.sub(pattern, '', upd_code)
            pattern =r' {2,}'
            clean_code = re.sub(pattern, '', clean_code)
            self.update_last_cell(path, clean_code.strip())
        elif "update_last_markdown" in router_action:
            text = self.get_last_cell(path)
            upd_markdown = self.markdown_update(text, query)
            pattern =r' {2,}'
            clean_text = re.sub(pattern, '', upd_markdown)
            self.update_last_markdown(path, clean_text)
        elif "update_selected_cell" in router_action:
            ind, code = self.get_cell_to_update(path)
            code = code.replace('## A MODIFIER ##', '')
            print(code)
            upd_code = self.code_update(query, code)
            upd_code = upd_code.replace('\_', '_').replace('`',"").replace("python", "")
            pattern =r'[=-]{2,}'
            clean_code = re.sub(pattern, '', upd_code)
            pattern =r' {2,}'
            clean_code = re.sub(pattern, '', clean_code)
            print(clean_code)
            self.update_cell(path, clean_code.strip(), ind)             
        elif "update_selected_markdown" in router_action:    
            ind, text = self.get_cell_to_update(path)
            text= text.replace('## A MODIFIER ##', '')
            upd_markdown = self.markdown_update(text, query)
            pattern =r'[=-]{2,}'
            clean_text = re.sub(pattern, '', upd_markdown)
            pattern =r' {2,}'
            clean_text = re.sub(pattern, '', clean_text)
            self.update_cell(path, clean_text, ind)    
        elif  "delete_last_cell" in router_action:
            self.delete_last_cell(path)
        elif "delete_selected_cell" in router_action:
            self.delete_cell(path, self.get_cell_to_delete(path))
        elif "explain_last_cell" in router_action:
            code = self.get_last_cell(path)
            explication = self.code_explanation(code)
            pattern =r' {2,}'
            clean_text = re.sub(pattern, '', explication)
            self.create_markdown(path, clean_text)
        elif "explain_selected_cell" in router_action:
            code = self.get_cell_to_explain(path)
            code = code.replace('## A EXPLIQUER ##', '')
            explication = self.code_explanation(code)
            pattern =r' {2,}'
            clean_text = re.sub(pattern, '', explication)
            self.create_markdown(path, clean_text)
        elif "summary_all" in router_action:
            list_codes = self.get_all_cell(self.path)
            combined_code = '\n'.join(cell for cell in list_codes)
            resume = self.chain_summary(combined_code)
            pattern =r' {2,}'
            clean_text = re.sub(pattern, '', resume)
            self.create_markdown(path, clean_text)
    
    def make_action(self, query) -> None:

        print(query)
        action = self.chain_router(query)
        self.tools(action, query, self.path)
    
    def last_version(self) -> None:
        #get the name of the notebook
        notebook_name = os.path.basename(self.path)
        #construct the backup path
        backup_path = os.path.join("backup", notebook_name)

        #get our file
        with open(backup_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)

        #save our notebbok with our old version
        self.save_notebook(self.path, nb)