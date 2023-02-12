import openai


class dummySearchEngine:
    def __init__(self):
        self.datas={"nginx install":"""
        to install nginx in debian,you just need to use this command:
        sudo apt install nginx
        if you are using root, you dont need sudo
        """,
        "nginx start":"Ai will not use this"
        }
    def search(self,keyword):
        ret=[]
        for i in self.datas.keys():
            if keyword in i:
                ret.append(i)
        return ret
    def read(self,keyword):
        return self.datas[keyword]
class Chat:
    def __init__(self,apitoken:str,context:bool=False,engine:str="text-davinci-002",searchengine=dummySearchEngine()):
        self.apitoken=apitoken
        openai.api_key=apitoken
        self.context=context
        self.engine=engine
        self.searchengine=searchengine
    def extract_keywords(self,question):
        completions = openai.Completion.create(
            engine="text-curie-001",
            prompt=f"Extract one keyword from the question: {question}",
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0,
        )

        keywords = completions.choices[0].text
        return keywords.strip()
    def select_best_result(self, question, results):
        completions = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Select the best result for the question: {question}\n" + "\n".join(results)+"\nAnswer:",
            temperature=0,
            max_tokens=150,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0.6
        )
        selected_result = completions.choices[0].text
        return selected_result.strip()
    def generate_response(self,prompt):
        completions = openai.Completion.create(
            engine="text-curie-001",
            prompt=prompt,
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.5,
        )

        message = completions.choices[0].text
        return message

    def talk(self,question):
        keyword=self.extract_keywords(question)
        items=self.searchengine.search(keyword)
        #print(items)
        infomations=self.searchengine.read(self.select_best_result(question,items))
        return self.generate_response(f'Answser the question "{question}" with the following infomations: "{infomations}"')
