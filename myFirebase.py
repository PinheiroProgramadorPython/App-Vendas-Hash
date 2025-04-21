import json
import requests
from kivy.app import App

class FireBase:

    API_KEY = 'AIzaSyAm0mGKxyDddR1Ug-yAKivK5YW4c6XCerY'
    def fazer_login(self,email,senha):
        link =f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.API_KEY}'
        info = {'email': email, 'password': senha, 'returnSecureToken': True}
        requicao = requests.post(link, data=info)
        requicao_dic = requicao.json()
        if requicao.ok:
            localId = requicao_dic['localId']
            idToken = requicao_dic['idToken']
            refreshToken = requicao_dic['refreshToken']

            meu_aplicativo = App.get_running_app()
            meu_aplicativo.localId = localId
            meu_aplicativo.idToken = idToken
            with open('refresh.txt', 'w') as arquivo:
                arquivo.write(refreshToken)
            meu_aplicativo.carregar_infos_usuario()
            meu_aplicativo.mudar_tela('homepage')

        else:
            mensagem_erro = requicao_dic['error']['message']
            meu_aplicativo = App.get_running_app()
            login_page = meu_aplicativo.root.ids['loginpage']
            login = login_page.ids['mensagem_login']
            login.text = mensagem_erro
            login.color = (1,0,0,1)
            meu_aplicativo.mudar_tela('loginpage')

    def trocarToken(self,refreshToken):
        link = f'https://securetoken.googleapis.com/v1/token?key={self.API_KEY}'
        info = {'grant_type':'refresh_token','refresh_token':refreshToken}
        requisicao = requests.post(link,data=info)
        requisicao_dict = requisicao.json()
        localId = requisicao_dict['user_id']
        idToken = requisicao_dict['id_token']
        return localId , idToken

    def criar_conta(self,email,senha):
        link = f'https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={self.API_KEY}'
        info = {'email':email,'password':senha,'returnSecureToken':True}
        requicao = requests.post(link,data=info)
        requicao_dic = requicao.json()
        if requicao.ok:
            localId = requicao_dic['localId']
            idToken = requicao_dic['idToken']
            refreshToken = requicao_dic['refreshToken']

            meu_aplicativo = App.get_running_app()
            meu_aplicativo.localId = localId
            meu_aplicativo.idToken = idToken
            with open('refresh.txt', 'w') as arquivo:
                arquivo.write(refreshToken)

            #requisição do id_proximo_usuario
            requicao_id = requests.get(f'https://aplicativovendashashtag-c22e2-default-rtdb.firebaseio.com/proximo_id_vendedor/.json')
            id_usuario = requicao_id.json()



            # requisição para adiconar o novo vendedor no banco de dados
            link_banco_dados = f'https://aplicativovendashashtag-c22e2-default-rtdb.firebaseio.com/{localId}.json'
            info_usuario = {'avatar':'foto1.png','equipe':f'{1}','total_vendas':0,'id_usuario':f'{id_usuario}','vendas':''}
            requicao_usuario = requests.patch(link_banco_dados,data=json.dumps(info_usuario))
            meu_aplicativo.carregar_infos_usuario()
            meu_aplicativo.mudar_tela('homepage')

            # atualizando proximo_id_vendedor
            id_usuario = int(id_usuario)+1
            info_id = {'proximo_id_vendedor':id_usuario}
            requicao_proximo_id_vendedor = requests.patch(f'https://aplicativovendashashtag-c22e2-default-rtdb.firebaseio.com/.json',data=json.dumps(info_id))

        else:
            mensagem_erro = requicao_dic['error']['message']
            meu_aplicativo = App.get_running_app()
            login_page = meu_aplicativo.root.ids['loginpage']
            login = login_page.ids['mensagem_login']
            login.text = mensagem_erro
            login.color = (1,0,0,1)
