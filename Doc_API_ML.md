Recomendações de Autenticação e Token
No Mercado Livre zelamos todos os dias pela segurança de nossos usuários na hora de lançar novas funcionalidades em nossa plataforma e além disso, queremos que sua aplicação também faça parte deste processo!
Na hora de desenvolver uma aplicação é importante estar atento à forma como o código está escrito, uma vez que podem haver brechas para fraude ou roubo de informações, por isso leve em consideraçãi as seguintes recomendações para mitigar vulnerabilidades.

Obter o access token enviando parâmetros através do body
Quando for realizar um POST ao recurso /oauth/token para obter acesso ao access token, você deverá enviar os parâmetros no body e não como querystring.
Isso permite que os dados sejam enviados de forma mais segura!


Exemplo:

curl -X POST \
-H 'accept: application/json' \
-H 'content-type: application/x-www-form-urlencoded' \
'https://api.mercadolibre.com/oauth/token' \
-d 'grant_type=authorization_code' \
-d 'client_id=$client_id' \
-d 'client_secret=$client_secret' \
-d 'code=$code' \
-d 'redirect_uri=$redirect_uri'
Access Token em todas as chamadas
Em toda chamada que você realizar à API do Mercado Livre, tenha em conta enviar o access token em todas elas para todos recursos tanto público como privados.

 

Gerar ID seguro para obter access token
Como uma medida opicional para aumentar a segurança nos processos para obter access tokens, recomendamos que você gere um valor randômico do tipo seguro e o envie como parâmetro state.
Por exemplo, para criar o secure_random ID em Java:

SecureRandom random = new SecureRandom();
Exemplo adicionando o valor ao parâmetro state:

curl -X  GET https://auth.mercadolibre.com.ar/authorization?response_type=code&client_id=$APP_ID&state=ABC123&redirect_uri=$REDIRECT_URL
Você receberá o código de autorização e também o ID seguro na URL de retorno:

https://YOUR_REDIRECT_URI?code=$SERVER_GENERATED_AUTHORIZATION_CODE&state=ABC123
Lembre-se de revisar o valor para assegurar-se que a resposta pertence a uma solicitação iniciada pela sua aplicação!

 

Utilização da mesma redirect URI
Lembre-se de enviar como redirect_uri a mesma URL que você colocou quando criou a aplicação!



Verifique aqui!

 

Validação de URLs para receber notificações
Em primeira instância valide a origem para saber que você está recebendo as notificações do Mercado Livre e não de outra fonte, então revise as URLs ao receber notificações para assegurar-se que os recursos que a sua aplicação vai consultar sejam válidos.

 

Access token em todos os pedidos
Em cada chamada que você fizer para a API do Mercado Livre, lembre-se de adicionar o token de acesso em todos os recursos, tanto públicos quanto privados e que seja correspondente ao usuário que a consulta.
Práticas de CyberSecurity
Nesta documentação você encontrará informações extras sobre diversas práticas que complementarão seu desenvolvimento seguro. Te Convidamos a considerá-los para melhorar consideravelmente a segurança de sua integração.

Auditoria e registro de logs
É essencial ter evidências concretas que nos permitam entender o que está acontecendo em nossa aplicação (para nos alertar) e o que aconteceu em determinado momento com determinado usuário, endpoint ou recurso.


Para implementar isso, temos diferentes alternativas possíveis:

Logging:o termo log é utilizado para se referir ao registro de eventos que estão ocorrendo ou já ocorreram em uma aplicação ou sistema. Geralmente, os eventos são de 5 tipos principais: informativos, debugging, warning, erro e alert.
Auditoría: é um conjunto de registros que evidencia o conjunto de atividades que afetaram um recurso ou evento ao longo do tempo.
Monitoreo: É uma ferramenta de diagnóstico que usamos para saber o status do pedido.

Advertências
Logging de dados confidenciais.

Deve ser evitado o logging de informações confidenciais, dados pessoais.


Proteção contra-ataques automatizados
Alguns casos em que queremos que um usuário possa usar alguma funcionalidade do nosso aplicativo, mas de forma limitada para evitar abusos da funcionalidade. Um exemplo claro disso pode ser o login: desejamos que o usuário possa inserir e-mail e senha para validar credenciais, mas também queremos evitar que usuários mal-intencionados abusem da funcionalidade enviando milhares de senhas e e-mails para validar usuários.


É importante mencionar que, neste caso, não estamos tentando nos defender contra-ataques de negação de serviço.


Rate Limiting
Rate Limiting é a prática de limitar o tráfico para o aplicativo ou seus componentes com base em uma determinada taxa. A ideia dessa prática é estabelecer um número finito de vezes que o usuário poderá utilizar para acessar a funcionalidade desejada. Por exemplo, “um usuário poderá fazer 5 transferências de dinheiro por hora”.

Referência de estratégias e técnicas de Rate Limit.


Captcha
O objetivo do CAPTCHA é evitar a automação, dando ao usuário a opção de “recuperar-se” da detecção de comportamento anormal, apresentando um desafio que somente um humano poderia resolver corretamente.



Em geral, a detecção de comportamento anômalo ou limites com base nos quais exibir o CAPTCHA é delegada ao mecanismo reCAPTCHA. Existe a alternativa reCAPTCHA v3 em que o serviço retorna uma scoring e podemos decidir quando mostrar ao usuário o desafio e quando não.

Referência de implementação reCAPTCHA.


Segredos
Às vezes é necessário usar algum segredo em nossas aplicações, por exemplo, credenciais de acesso a um banco de dados, uma key para consumir algum serviço ou algum valor aleatório para assinar mensagens.


Nesses casos, pode ocorrer uma má prática de deixar segredos codificados no código. Isso torna o segredo disponível para todos com acesso a ele.


Como implementá-lo?
Melhores práticas para o armazenamento de segredos ou keys, indicam que você deve usar as variáveis de entorno para armazenar os segredos, ou utilizar um alojamento externo ao código-fonte do aplicativo, onde são armazenadas todas as credenciais para seu funcionamento.


A mesma hospedagem pode ser arquivos de configuração, bases de dados ou serviços especializados para o armazenamento de segredos como os disponíveis nos serviços dos diferentes provedores de nuvem, e deve ser fortemente protegido contra acesso de terceiros, incluindo outros usuários locais no mesmo sistema.


Advertências
Muitas vezes, ao utilizar sistemas de versionamento, por erro, deixamos o segredo no código e, percebendo, fazemos um novo commit. Ao fazer isso, o segredo permanece no repositório.


Recomendamos que, se um segredo tiver sido codificado permanentemente, ele seja removido do código conforme as recomendações acima e substituído por um novo. Caso isso não seja possível, recomendamos que você remova o commit afetado guia para Github.


Dependências de software de terceiros
Em muitas ocasiões, as dependências de terceiros que incluímos em nosso software apresentam vulnerabilidades ou são diretamente maliciosas.


Por esses motivos, é muito importante prestarmos atenção à segurança dos componentes de terceiros que incluímos, portanto, ao escolher uma dependência, deve-se escolher a versão mais recente sem vulnerabilidades encontradas.


Criptografia Aplicada
Antes de aplicar qualquer técnica criptográfica, é necessário analisar o tipo de dados a serem protegidos e seu estado (em repouso, em trânsito ou em uso) para garantir que a técnica a ser utilizada resolva a necessidade que se exige. Em geral, se ao analisar o tipo de dados que precisam ser protegidos, identifica-se que:

Deve ser reversível (retornar ao seu estado original), o que deve ser aplicado é uma técnica de criptografia.
Não deve ser reversível, a técnica apropriada é o hashing.
Requer garantia de não repúdio, a técnica adequada é a assinatura digital.

Propiedade	Mecanismo	Entidades	Implementação
Confidencialidade + autenticidade	Criptografia	Mesmo aplicativo ou projeto	AES-GCM-256.
Integridade + autenticidade	MAC	Mesmo aplicativo / Múltiplos	HMAC-SHA256
Integridade + autenticidade Não repudio	Assinatura digital	Múltiplos Aplicativos / Entidades Externas	Ed25519

Siguiente: Validações e requisitos de segurança.
Validações e requisitos de segurança
Nesta documentação você encontrará práticas de segurança a serem implementadas que são essenciais para sua integração. Implementá-los permitirá fortalecer o núcleo dos processos de segurança do seu desenvolvimento.

Requisitos específicos
Autenticação
A autenticação é um processo que permite conhecer a identidade digital de um usuário (previamente cadastrado) e consiste em uma série de mecanismos que estabelecem que esse usuário é quem diz ser. Esses mecanismos são geralmente agrupados em 3 grandes categorias:

Algo que eu sei (senha).
Algo que eu tenho (telefone celular, token de autenticação, yubikey).
Algo que eu sou (biometria).

A combinação desses fatores é o que gera uma autenticação robusta.



Autorização
A autorização é o mecanismo pelo qual controlamos o acesso a um recurso, geralmente com base em uma identidade de usuário previamente validada. É importante diferenciar esse processo de autenticação: a finalidade da autenticação é determinar a identidade de um usuário, enquanto a finalidade da autorização é determinar se essa identidade possui permissões suficientes para executar a ação que está tentando realizar. Essas validações devem ser implementadas no Backend.

Existem inúmeras metodologias para construir matrizes de autorização. Entre os mais conhecidos estão RBAC, ABAC, ACL, MAC, entre outros.





Validação de data
A validação de dados é a prática que nos permite validar que todos os valores que não se originam em nosso aplicativo estão bem formados, tanto semanticamente quanto sintaticamente, antes de processá-los, salvá-los ou transmiti-los.


Como regra geral e para segurança da aplicação, a validação de dados deve ser implementada nos serviços de backend, pois são fluxos que não podem ser modificados pelo usuário final, diferentemente das validações de frontend que respondem apenas a uma boa resposta.


É uma prática comum realizar a validação de entrada no front-end (lado do cliente), por exemplo, não permitir que o usuário prossiga no fluxo se não colocar algo na forma de um e-mail em um campo de e-mail. Isso é válido do ponto de vista funcional, mas temos que considerar que, ao nível de segurança, um usuário pode ignorar validações do lado do cliente e, assim, enviar dados maliciosos para aplicativos. Por esse motivo, todas as validações de entrada que realizamos no lado do cliente também devem ser feitas no lado do servidor. .


Validação sintática
Por validação sintática queremos dizer que o valor é formado corretamente em relação ao tipo ou estrutura de dados esperados.


Para tipos de dados primitivos, como float, double, char, boolean, short or long, uma estratégia recomendada é executar typecasting. A ideia simplificada é a seguinte: HTTP é um protocolo baseado em texto, então todo valor de tipo básico chegando em um request é fundamentalmente uma String (ou array de caracteres) com uma certa codificação.


Na etapa sintática, nosso objetivo é converter a String para os valores essenciais correspondentes que estamos esperando. Por exemplo:


Se esperamos um user_id, que sabemos ser um Int,podemos realizar a validação de estilo:



Validação semântica
A validação semântica envolve entender se o valor está correto em termos do contexto em que está sendo usado.

No contexto de tipos de dados básicos, podemos pensar em exemplos como os seguintes:

O valor de uma transação não deve ser negativo e deve ter no máximo dois zeros de arredondamento.
Um número de pedido não deve ser negativo e deve ser um número inteiro.
Um sobrenome não deve ter caracteres especiais ou não imprimíveis.
A data de nascimento de um usuário não deve ser inferior ao ano de 1900.

No contexto de tipos de dados complexos, podemos pensar nos seguintes exemplos:

Por mais que um documento de escritório esteja bem formado, temos que verificar se ele possui macros presentes com código potencialmente vulnerável ou malicioso.
Se estivermos recebendo imagens, determine qual é o peso máximo e mínimo que elas devem ter, se devemos excluir a metadata ou se contém apenas informações relacionadas a uma imagem.

Advertências
Allow list vs Block list
Nas metodologias de validação podemos utilizar duas grandes estratégias: Block list e Allow List.Em termos simples, uma metodologia blocklist consiste em definir e buscar todos os valores inesperados para cada entrada. Por exemplo:



O problema geral dessa estratégia é que é complexo conhecer todos os caracteres perigosos ou inesperados, embora hoje tenhamos toda a lista, as tecnologias e padrões mudam, deixando a blocklist possivelmente desatualizada e vulnerável.


Em vez disso, é recomendável usar uma estratégia de Allow list que consiste em definir os caracteres ou formatos de input esperados pelo aplicativo. O racional é o seguinte, é muito mais fácil conhecer e definir quais dados estou esperando do que saber o que não estou esperando.


Seguindo essa estratégia, devemos ser o mais restritivos possível, evitando a todo momento, receber dados de entrada que contenham, por exemplo: "." ou "/".


Caso a lista de caracteres seja muito permissiva porque o aplicativo a exige, será necessário implementar controles adicionais, para evitar comportamentos indesejados.


Por exemplo:


Se o parâmetro for direcionado de uma consulta para um banco de dados, é necessário parametrizar as consultas.
Se o parâmetro que esperamos for altamente específico, devemos implementar expressões regulares para validar os dados esperados.
Se o parâmetro é retornado ao frontend, devem ser implementadas validações adicionais, como: codificação ou sanitização.

Requerimentos gerais
A seguir, uma tabela de resumo é fornecida para uso como uma check-list.


Resumen de los recursos disponibles
Controle	Descrição

Autenticação

Validar que todas as funcionalidades do aplicativo estão autenticadas, que a solicitação foi solicitada por um usuário legítimo.

Autorização

Validar se o usuário autenticado anteriormente tem permissões para acessar ou modificar o recurso específico.

Validação de dados	
Certificar que todos os valores ou parâmetros sejam validados semântica e sintaticamente antes de serem usados. Preste atenção aos tipos de dados e use um modelo de allow list (valores permitidos) antes da blocklist (valores não permitidos).

Auditoría e registro de logs

Validar se é possível responder "Quem fez o quê, de onde, quando e com que resultado" com os logs disponíveis em cada funcionalidade do aplicativo. Evite o "logging" de informações do usuário (PII) ou confidenciais.
Proteção contra ataques automatizados	
Validar se todas as funcionalidades de modificação de recursos (POST, PUT, DELETE) possuem mecanismos para evitar ataques automatizados, como força bruta ou enumeração de informações.

Segredos

Validar se nenhum segredo está “hardcodeado” no código. Os segredos incluem credenciais de acesso, tokens de autenticação, certificados digitais e qualquer outro tipo de informação confidencial. Todos os segredos devem ser guardados e consumidos por mecanismos adequados ao seu tratamento.

Dependências de software de terceiros

Validar se as dependências externas não possuem vulnerabilidades.

Criptografía Aplicada

Validar se os esquemas de hashing, cifrado, assinatura ou geração de sequência random estão sendo usados corretamente, e adequadas para resolver o caso de uso particular.
Gerencie seu aplicativo
Detalhes dos aplicativos
Para acessar todos os detalhes de um de seus aplicativos, basta incluir o app_id na chamada à API.


Chamada:

curl -X GET -H 'Authorization: Bearer $ACCESS_TOKEN' https://api.mercadolibre.com/applications/$APP_ID
Exemplo:

curl -X GET -H 'Authorization: Bearer $ACCESS_TOKEN' https://api.mercadolibre.com/applications/12345
Resposta:

{
  "id": 213123928883922,
  "site_id": "MLB",
  "thumbnail": null,
  "url": "http://apps.mercadolivre.com.br/polipartes",
  "sandbox_mode": true,
  "project_id":null,
  "active": true,
  "max_requests_per_hour": 18000,
  "certification_status": "not_certified"
}
Dados privados do seu aplicativo
Sempre que você quiser saber mais detalhes dos dados de seu aplicativo, faça isso usando o token de acesso do usuário com quem ele foi criado.


Chamada:

curl -X GET -H 'Authorization: Bearer $ACCESS_TOKEN' https://api.mercadolibre.com/applications/$APP_ID
Exemplo:

curl -X GET -H 'Authorization: Bearer $ACCESS_TOKEN' https://api.mercadolibre.com/applications/12345
Aplicativos autorizadas por usuário
Para acessar todos os aplicativos autorizados por um usuário, basta enviar uma solicitação GET com o user_id e o token de acesso.


Chamada:

curl -X GET -H 'Authorization: Bearer $ACCESS_TOKEN' https://api.mercadolibre.com/users/$USER_ID/applications
Exemplo:

curl -X GET -H 'Authorization: Bearer $ACCESS_TOKEN' https://api.mercadolibre.com/users/26317316/applications
A resposta será um conjunto de aplicativos no seguinte formato:

[
  - {
  "user_id": "26317316",
  "app_id": "13795",
  "date_created": "2012-12-20T15:38:27.000-04:00",
  "scopes": - [
    "read",
    "write",
  ],
   },
]
Usuários que deram permissões ao seu aplicativo
Para acessar a lista de usuários que deram permissões ao seu aplicativo, faça o GET a seguir:


Exemplo:

curl -X GET -H 'Authorization: Bearer $ACCESS_TOKEN' https://api.mercadolibre.com/applications/$APP_ID/grants
Resposta:

{
    "paging": {
        "total": 1,
        "limit": 50,
        "offset": 0
    },
    "grants": [
        {
            "user_id": {user_id},
            "app_id": {app_id},
            "date_created": "2012-05-19T01:00:54.000-04:00",
            "scopes": [
                "read",
                "offline_access",
                "write"
            ]
        }
    ]
}
Descrição de campos
user_id: identificador do usuário.
app_id: identificador do aplicativo.
date_created: data em que a autorização foi criada.
scopes: permissões concedidas ao aplicativo: leitura, gravação e offline_access.
Considerações
No DevCenter, a partir da tela de "Administrar permissões", é possível visualizar e exportar a lista de Grants que a aplicação possui.
Esses são os possíveis estados para as permissões da integração:

Novo: Grant gerado há menos de 24 horas.
Ativo: usuário com uso ativo de nossas APIs nos últimos 90 dias.
Inativo: usuário considerado inativo, pois não houve chamadas aos recursos do nosso ecossistema MeLi nos últimos 90 dias.


Revogar a autorização do usuário
Para eliminar qualquer aplicativo, é preciso especificar seu ID, o ID do usuário e o token de acesso. Basta enviar uma solicitação DELETE utilizando a consulta abaixo:

curl -X DELETE -H 'Authorization: Bearer $ACCESS_TOKEN' https://api.mercadolibre.com/users/$USER_ID/applications/$APP_ID
A resposta deve ser:

{
    "user_id":"{user_id}",
    "app_id":"{app_id}",
    "msg":"Autorización eliminada"
}
Métricas de consumo da aplicação
Para acessar o detalhe de todo o consumo dos recursos do MeLi por sua aplicação, simplemente realiza o seguinte GET:

curl -X GET -H 'Authorization: Bearer $ACCESS_TOKEN' https://api.mercadolibre.com/applications/v1/$APP_ID/consumed-applications?date_start=2025-08-01&date_end=2025-08-20
Resposta:

{
    "app_id": 5555737222442288,
    "total_request": 3773948444,
    "request_by_status": [
        {
            "total_request": 1,
            "status": 412,
            "percentage": 0
        },
        {
            "total_request": 108,
            "status": 502,
            "percentage": 0.0000029
        },
        {
            "total_request": 253,
            "status": 534,
            "percentage": 0.0000067
        },
        {
            "total_request": 680,
            "status": 423,
            "percentage": 0.000018
        },
        {
            "total_request": 15587,
            "status": 503,
            "percentage": 0.000413
        },
        {
            "total_request": 19393,
            "status": 405,
            "percentage": 0.0005139
        },
        {
            "total_request": 56464,
            "status": 499,
            "percentage": 0.0014962
        },
        {
            "total_request": 64834,
            "status": 204,
            "percentage": 0.0017179
        },
        {
            "total_request": 74716,
            "status": 535,
            "percentage": 0.0019798
        },
        {
            "total_request": 150226,
            "status": 500,
            "percentage": 0.0039806
        },
        {
            "total_request": 202157,
            "status": 409,
            "percentage": 0.0053566
        },
        {
            "total_request": 425759,
            "status": 422,
            "percentage": 0.0112815
        },
        {
            "total_request": 638862,
            "status": 201,
            "percentage": 0.0169282
        },
        {
            "total_request": 1999743,
            "status": 400,
            "percentage": 0.0529881
        },
        {
            "total_request": 4764611,
            "status": 429,
            "percentage": 0.12625
        },
        {
            "total_request": 7441701,
            "status": 206,
            "percentage": 0.1971861
        },
        {
            "total_request": 12630990,
            "status": 401,
            "percentage": 0.334689
        },
        {
            "total_request": 29612527,
            "status": 404,
            "percentage": 0.7846564
        },
        {
            "total_request": 91749024,
            "status": 403,
            "percentage": 2.4311149
        },
        {
            "total_request": 3624100808,
            "status": 200,
            "percentage": 96.0294202
        }
    ],
    "top_apis_consumed": [
        {
            "resource_id": "read.items-visits",
            "resource_name": "METRICAS",
            "hierarchy1": "VISITAS",
            "hierarchy2": "VISITAS_USUARIOS_ITEMS",
            "percentage_request_successful": 94.4858993
        },
        {
            "resource_id": "public-read.items-prices-api",
            "resource_name": "PUBLICA_SINCRONIZA",
            "hierarchy1": "PRECIOS",
            "hierarchy2": "CONSULTAR_PRECIOS",
            "percentage_request_successful": 99.6489243
        },
        {
            "resource_id": "items-public.multigetapi",
            "resource_name": "PUBLICA_SINCRONIZA",
            "hierarchy1": "ITEMS",
            "hierarchy2": "BUSQUEDA_MULTIGET",
            "percentage_request_successful": 99.952714
        },
        {
            "resource_id": "public.pc-open-platform-api",
            "resource_name": "COMUNICACION",
            "hierarchy1": "RECLAMOS",
            "hierarchy2": "DETALLES_DEVOLUCION",
            "percentage_request_successful": 91.8956306
        },
        {
            "resource_id": "public.pc-open-platform-api",
            "resource_name": "COMUNICACION",
            "hierarchy1": "RECLAMOS",
            "hierarchy2": "DETALLES_DEVOLUCION",
            "percentage_request_successful": 0.0014296
        },
        {
            "resource_id": "public.shipping-mandatory-api",
            "resource_name": "VENTAS_ENVIOS",
            "hierarchy1": "COSTOS_ENVIOS_SLA",
            "hierarchy2": "CONSULTAR_COSTOS_ENVIOS",
            "percentage_request_successful": 99.8737551
        },
        {
            "resource_id": "public.shipping-shipments-api",
            "resource_name": "VENTAS_ENVIOS",
            "hierarchy1": "MERCADO_ENVIOS",
            "hierarchy2": "GESTIONAR_ENVIOS",
            "percentage_request_successful": 99.9241283
        },
        {
            "resource_id": "public-postsale-read.supply-messages-gateway",
            "resource_name": "MENSAJERIA",
            "hierarchy1": "MOTIVOS",
            "hierarchy2": "CONSULTAR_MOTIVOS_Y_MENSAJES_POR_ID",
            "percentage_request_successful": 99.8578694
        }
    ],
    "top_apis_consumed_error": [
        {
            "resource_id": "public.pc-open-platform-api",
            "errors_by_resource_id": 9272595,
            "resource_name": "COMUNICACION",
            "hierarchy1": "RECLAMOS",
            "hierarchy2": "DETALLES_DEVOLUCION",
            "percentage_errors": 8.1029398
        },
        {
            "resource_id": "read.items-visits",
            "errors_by_resource_id": 4200509,
            "resource_name": "METRICAS",
            "hierarchy1": "VISITAS",
            "hierarchy2": "VISITAS_USUARIOS_ITEMS",
            "percentage_errors": 5.5141007
        },
        {
            "resource_id": "public-read.items-prices-api",
            "errors_by_resource_id": 2041039,
            "resource_name": "PUBLICA_SINCRONIZA",
            "hierarchy1": "PRECIOS",
            "hierarchy2": "CONSULTAR_PRECIOS",
            "percentage_errors": 0.3510757
        },
        {
            "resource_id": "public-postsale-read.supply-messages-gateway",
            "errors_by_resource_id": 135181,
            "resource_name": "MENSAJERIA",
            "hierarchy1": "MOTIVOS",
            "hierarchy2": "CONSULTAR_MOTIVOS_Y_MENSAJES_POR_ID",
            "percentage_errors": 0.1421306
        },
        {
            "resource_id": "public.shipping-mandatory-api",
            "errors_by_resource_id": 912460,
            "resource_name": "VENTAS_ENVIOS",
            "hierarchy1": "COSTOS_ENVIOS_SLA",
            "hierarchy2": "CONSULTAR_COSTOS_ENVIOS",
            "percentage_errors": 0.1262449
        },
        {
            "resource_id": "public.shipping-shipments-api",
            "errors_by_resource_id": 600915,
            "resource_name": "VENTAS_ENVIOS",
            "hierarchy1": "MERCADO_ENVIOS",
            "hierarchy2": "GESTIONAR_ENVIOS",
            "percentage_errors": 0.0758717
        },
        {
            "resource_id": "items-public.multigetapi",
            "errors_by_resource_id": 376990,
            "resource_name": "PUBLICA_SINCRONIZA",
            "hierarchy1": "ITEMS",
            "hierarchy2": "BUSQUEDA_MULTIGET",
            "percentage_errors": 0.047286
        }
    ]
}
Considerações
O parâmetro de data é opcional. Caso não seja informado, o recurso retorna os dados de consumo dos últimos 15 dias.
A informação é atualizada como D-1, ou seja, você sempre terá o consumo até o dia anterior à data atual.
Recomendamos que as buscas sejam feitas com intervalos mensais e não por intervalos muito grandes, pois, devido à quantidade de dados, a busca pode demorar muito e resultar em um erro de “timeout”.
Autenticação e Autorização
Para começar a utilizar nossos recursos, você deve desenvolver os processos de Autenticação e Autorização. Assim, você poderá trabalhar com os recursos privados do usuário quando autorize seu aplicativo.

Enviar access token no header
Por segurança, você deve enviar o token de acesso por header toda vez que fizer chamadas para a API. O header da autorização será:
curl -H 'Authorization: Bearer APP_USR-12345678-031820-X-12345678' \
Por exemplo, fazer um GET para o recurso /users/me seria:
curl -H 'Authorization: Bearer APP_USR-12345678-031820-X-12345678' \
https://api.mercadolibre.com/users/me
Saiba mais sobre a segurança do seu desenvolvimento.


Autenticação
O processo de autenticação é utilizado para verificar a identidade de uma pessoa em função de um ou vários fatores, garantindo que os dados de quem os enviou sejam corretos. Ainda que existam diferentes métodos, em Mercado Livre utilizamos o baseado em senhas.


Autorização
A autorização é o processo por meio do qual permitimos acessar a recursos privados. Nesse processo deverá ser definido que recursos e operações podem ser realizados (“só leitura” ou “leitura e escrita”).


Como obtemos a autorização?
Por meio do Protocolo OAuth 2.0, um dos mais utilizados em plataformas abertas (Twitter, Facebook, etc.) e método seguro para trabalhar com recursos privados.


Este protocolo nos oferece:

Confidencialidade, o usuário nunca deverá revelar sua senha.
Integridade, apenas poderão ver dados privados os aplicativos que tiverem permissão para fazê-lo.
Disponibilidade, os dados sempre serão disponibilizados no momento em que forem necessários.

O protocolo de operação é chamado de Grant Types, e o utilizado é The Authorisation Code Grant Type (Server Side).


A seguir mostraremos a você como trabalhar com os recursos de Mercado Livre utilizando Implicit Grant Type.


Server side
O fluxo Server side é o mais adequado para os aplicativos que executam código do lado do server. Por exemplo, aplicativos desenvolvidos em linguagens como Java, Grails, Go, etc.


Em resumo, o processo que estará realizando é o seguinte:

flujo_serverside_por
 Redireciona o aplicativo para Mercado Livre.
 Não se preocupe com a autenticação dos usuários no Mercado Livre, nossa plataforma tomará conta disso!
Página de autorização.
 POST para alterar o código de autorização por um access token.
 O API de Mercado Libre altera o código de autorização por um token.
 Já pode utilizar o access token para realizar chamadas ao nosso API e acessar os dados privados do usuário.


Passo a passo:
1. Realizando autorização
1.1. Conecte-se com seu usuário de Mercado Livre:



Notas:
- Você pode usar um usuário de teste.
- Lembre que o usuário que inicie sessão deve ser administrador, para que o access token obtido tenha as permissões suficientes para realizar as consultas.
- Se o usuário for operador/colaborador, o grant será inválido e vai receber o erro invalid_operator_user_id.
- Os eventos a seguir podem invalidar um access token antes do tempo de expiração:

Alteração da senha pelo usuário.
Atualização do Client Secret por um aplicativo.
Revogação de permissões para seu aplicativo pelo usuário.
Se não utilizar a aplicação com alguma chamada em https://api.mercadolibre.com/ durante 4 meses.

Importante:
A redirect_uri deve corresponder exatamente ao que está registrado nas configurações do seu aplicativo para evitar erros de acesso; a url não pode conter informações variáveis.
1.2. Coloque o seguinte URL na janela de seu navegador para obter a autorização:

https://auth.mercadolivre.com.br/authorization?response_type=code&client_id=$APP_ID&redirect_uri=$YOUR_URL&code_challenge=$CODE_CHALLENGE&code_challenge_method=$CODE_METHOD
No exemplo, utilizamos a URL para Brasil (mercadolivre.com.br), porém, se estiver trabalhando em outros países, lembre-se de alterar pelo domínio do país correspondente. Por exemplo, Uruguay: mercadolibre.com.uy. Ou Argentina: mercadolibre.com.ar. Veja os países em que operamos.


Parâmetros
response_type: enviando o valor “code” será obtido um access token que permitirá ao aplicativo interagir com Mercado Livre.
redirec_URI: o atributo YOUR_URL é completado com o valor adicionado quando quando o aplicativo for criado.Deve ser exatamente igual ao que você configurou e não pode ter informações variáveis.



client_id: uma vez criado o aplicativo, será identificado como APP ID.


State: para aumentar a segurança, recomendamos que você inclua o parâmetro de estado na URL de autorização para garantir que a resposta pertença a uma solicitação iniciada por seu aplicativo.
Caso você não tenha um identificador aleatório seguro, você pode criá-lo usando SecureRandom e deve ser exclusivo para cada tentativa de chamada.
Portanto, a URL de redirecionamento será:

https://auth.mercadolivre.com.br/authorization?response_type=code&client_id=1620218256833906&redirect_uri=https://localhost.com/redirect&state=$12345
Um uso adequado para o parâmetro state é enviar um estado que você precisará saber quando a URL definida no redirect_uri é chamada. Lembre-se que o redirect_uri deve ser uma URL estática então se você está pensando em enviar parâmetros nesta URL use o parâmetro state para enviar esta informação, caso contrário a requisição irá falhar pois o redirect_uri não corresponde exatamente ao configurado em sua aplicação.


Os parâmetros a seguir são opcionais e só se aplicam se o aplicativo tiver o fluxo de PKCE (Proof Key for Code Exchange) habilitado, Entretanto ao ser ativada esta opção, o envio do campo se torna obrigartório.

code_challenge:: código de verificação gerado a partir de code_verifier y cifrado com code_challenge_method.

code_challenge_method:: método usado para gerar o code challenge. Os seguintes valores são suportados atualmente:

S256: especifica que o code_challenge encontrase-se usando o algoritmo de cifrado SHA-256.
plain: o mesmo code_verifier é enviado como code_challenge. Por razões de segurança, não é recomendado usar este método.
O redirect_uri tem que corresponder exatamente ao inserido quando o aplicativo foi criado para evitar o seguinte erro,dessa forma, não pode conter informações variáveis:



Descrição: your client callback has to match with the redirect_uri param.


1.3. Como último passo do usuário, ele será redirecionado para a tela seguinte, onde lhe será requerido que autorize o aplicativo à sua conta.



Notas:
Adicionamos informações do DPP (nível integrador) informando ao vendedor se o aplicativo é certificado ou não.

Conferindo a URL, se pode observar que o parâmetro CODE foi adicionado.

https://YOUR_REDIRECT_URI?code=$SERVER_GENERATED_AUTHORIZATION_CODE&state=$RANDOM_ID
Exemplo:

https://localhost.com/redirect?code=TG-61828b7fffcc9a001b4bc890-314029626&state=ABC1234
Este CODE será utilizado para gerar um access token, que permitirá acessar a API.

Nota:
- Considere que se o usuário for operador/colaborador, NÃO será possível realizar o grant para a aplicação. Vai retornar o erro invalid_operator_user_id.
Lembre-se de verificar esse valor para certificar-se de que a resposta pertence a uma solicitação iniciada por seu aplicativo, pois o Mercado Livre não valida este campo.


1.4 Se você receber a mensagem de erro: Sorry, the application cannot connect to your account. (Desculpe, o aplicativo não pode se conectar à sua conta), as seguintes considerações devem ser feitas:



1. A redirect_uri deve corresponder exatamente ao que está registrado nas configurações do seu aplicativo para evitar erros de acesso; a url não pode conter informações variáveis.

2. Valide se o token e a concessão do appid são válidos.

3. Verifique se o vendedor está fazendo login com a conta principal e não com um colaborador.

4. Verifique se o vendedor ou owner da aplicação possuem dados pendentes de validação , ou alguma inabilitação na conta.


2. Trocando o code por um token
Para que o código de autorização seja trocado por um access token, você deve realizar um POST enviando os parâmetros por BODY:

curl -X POST \
-H 'accept: application/json' \
-H 'content-type: application/x-www-form-urlencoded' \
'https://api.mercadolibre.com/oauth/token' \
-d 'grant_type=authorization_code' \
-d 'client_id=$APP_ID' \
-d 'client_secret=$SECRET_KEY' \
-d 'code=$SERVER_GENERATED_AUTHORIZATION_CODE' \
-d 'redirect_uri=$REDIRECT_URI' \
-d 'code_verifier=$CODE_VERIFIER' 
Parâmetros
grant_type: authorization_code indica que a operação desejada é mudar o “code” por um access token.
client_id: é o APP ID do aplicativo que foi criado.
client_secret: é a Secret Key que foi gerado ao criar o aplicativo.
code: o código de autorização obtido no passo anterior.
redirect_uri: o redirect URI configurado para seu aplicativo não pode conter informações variáveis.


O seguinte parâmetro e opcionais só se aplicam se o aplicativotiver o fluxo de PKCE (Proof Key for Code Exchange).

code_verifier: sequência de caracteres aleatória com a qual o code_challenge foi gerado. Isso será usado para verificar e validar a solicitação.


Resposta:

{
    "access_token": "APP_USR-123456-090515-8cc4448aac10d5105474e1351-1234567",
    "token_type": "bearer",
    "expires_in": 21600,
    "scope": "offline_access read write",
    "user_id": 1234567,
    "refresh_token": "TG-5b9032b4e23464aed1f959f-1234567"
}
Pronto! Você já pode usar o access token para fazer chamadas a nossa API e acessar os recursos privados do usuário.


3. Refresh token
Considere que o access token gerado expirará após 6 horas, desde solicitado. Por isso, para garantir que possa trabalhar por um tempo prolongado e não seja necessário solicitar constantemente ao usuário que volte a se logar para gerar um token novo, oferecemos a solução de trabalhar com um refresh token. Além disso, lembre-se de que o refresh_token é de utilização única e que será devolvido um novo refresh_token em cada processo de atualização executado.


Cada vez que fizer a chamada que muda o code por um access token, também terá o dado de um refresh_token, que deverá guardar para trocá-lo por um access token quando expirado. Para renovar seu access token deverá realizar a chamada seguinte:
curl -X POST \
-H 'accept: application/json' \
-H 'content-type: application/x-www-form-urlencoded' \
'https://api.mercadolibre.com/oauth/token' \
-d 'grant_type=refresh_token' \
-d 'client_id=$APP_ID' \
-d 'client_secret=$SECRET_KEY' \
-d 'refresh_token=$REFRESH_TOKEN'
Parâmetros
grant_type: refresh_token Indica que a operação desejada é atualizar um token.
refresh_token: o refresh token do passo de aprovação guardado previamente.
client_id: é o APP ID do aplicativo que foi criado.
client_secret: é o APP ID do aplicativo que foi criado.


Reposta:

{
    "access_token": "APP_USR-5387223166827464-090515-b0ad156bce700509ef81b273466faa15-8035443",
    "token_type": "bearer",
    "expires_in": 21600,
    "scope": "offline_access read write",
    "user_id": 8035443,
    "refresh_token": "TG-5b9032b4e4b0714aed1f959f-8035443"
}
A resposta inclui um novo access token válido por mais 6 horas e um novo REFRESH_TOKEN que deverá guardar para utilizá-lo cada vez que expirar.

Importante:
- Permitimos usar apenas o último REFRESH_TOKEN gerado para fazer o intercâmbio.
- O REFRESH_TOKEN só pode ser usado uma vez e somente pelo client_id ao qual está associado, depois de ser usado ele se tornará inválido.
- Para otimizar os processos de seu desenvolvimento, sugerimos que renove seu access token somente quando perder validade.



Referencia de códigos de erro
1. invalid_client: o client_id e/ou client_secret do seu aplicativo fornecido é inválido.
2. invalid_grant: os motivos são vários: pode ser porque o authorization_code ou refresh_token são inválidos, expiraram ou foram revogados, foram enviados em um fluxo incorreto, pertencem a outro cliente ou o redirect_uri usado no fluxo de autorização não corresponde ao que tem configurado seu aplicativo, ou o usuário (vendedor) possui a pendencia de incluir dados e/ou documentos.
3. invalid_scope: o alcance solicitado é inválido, desconhecido ou foi criado no formato errado. Os valores permitidos para o parâmetro alcance são: “offline_access”,”write” e ”read”.
4. invalid_request: a solicitação não inclui um parâmetro obrigatório, inclui um parâmetro ou valor de parâmetro não suportado, tem algum valor dobrado ou está mal formado.
5. unsupported_grant_type: os valores permitidos para grant_type são “authorization_code” ou “refresh_token”.
6. forbidden (403): a chamada não autoriza o acesso, possivelmente está sendo usado o token de outro usuário, ou o IP esta bloqueado ou faltam scopes. Para o caso de grant o usuário não tem acesso à URL de Mercado Livre de seu país (.ar, .br, .mx, etc) e deve verificar que sua conexão ou navegador funcione corretamente para os dominios do MELI
7. local_rate_limited (429): por excessivas requisições, são bloqueadas temporariamente as chamadas. Volte a tentar em alguns segundos.
8. unauthorized_client: a aplicação não tem grant com o usuário ou as permissões (scopes) que tem o aplicativo com esse usuári. Não permitem criar um token.
9. unauthorized_application: a aplicação está bloqueada, e por isso não poderá operar até resolver o problema.


Erro Invalid Grant
Durante o fluxo obter o refresh token ou authorization code, é possível obter o erro invalid_grant com a mensagem "Error validating grant. Your authorization code or refresh token may be expired or it was already used"

    {
    "error_description": "Error validating grant. Your authorization code or refresh token may be expired or it was already used",
    "error": "invalid_grant",
    "status": 400,
    "cause": []
}
Essa mensagem indica que o authorization_code ou refresh_token não existem, ou foram excluídos. Alguns dos motivos são:

Tempo de Expiração: passado o tempo de duração do refresh_token (6 meses), vai expirar automaticamente e será necessário fazer de novo o fluxo para obter um novo refresh_token.
Revogação da autorização: ao revogar a autorização entre a conta do seller e seu aplicativo (seja por parte do integrador ou do vendedor), os access_token e refresh_token serão invalidados. É possível verificar os usuários que não tem grant com sua aplicação desde a opção "Administrar Permissões" (no painel Meus Aplicativos), ou utilizando a chamada para acessar aos usuários que outorgaram permissões ao seu aplicativo.
Revogação interna: existem alguns fluxos internos que causam a exclusão das credenciais dos usuários, impedindo que os integradores possam continuar trabalhando em nome dos vendedores; nesses casos, é necessário completar de novo o fluxo de autorização/autenticação. Esses fluxos são disparados principalmente por exclusão das seções dos usuários. Os motivos são vários, mas os mais comuns são alteração de senha, desvinculação de dispositivos ou fraude. Saiba como revogar a autorização de um usuário para sua aplicação.
Importante:
Considere que para esse último fluxo, apenas detalhamos alguns exemplos, não todos os casos disponíveis.

Seguinte: Consulta API Docs.
Realização de testes
O Mercado Livre não tem um ambiente para teste ou sandbox. Disponibilizamos usuários de teste para verificação direta em ambiente de produção. A vantagem de trabalhar com usuários de teste, é que você pode fazer simulações entre esses usuários com as mesmas ações habilitadas para usuários reais: publicar, atualizar dados, perguntar, responder, comprar, vender, opinar, etc., sem pagar nada ou ser sancionado e, evitando prejudicar a reputação de um usuário real. Com este tutorial, você poderá começar a trabalhar com nossa API enquanto seu aplicativo se encontrar em fase de desenvolvimento.

Importante:
Todas as transações de teste devem ser realizadas entre usuários de teste. Reforçamos que contas pessoais ou de familiares não devem ser, em hipótese alguma, utilizadas para testes.

Criação de um usuário de teste
Para criar um usuário de teste, você deve ter um token. Se ainda não tiver seu ACCESS_TOKEN, você poderá começar aqui: Guia de Autenticação e Autorização. No JSON, você só deve enviar o ID do país onde quer operar. Consulte nossa API de sites da nossa API para conhecer o site_id de cada país. Recomendamos a criação de pelo menos um usuário vendedor e um usuário comprador, para realizar transações entre eles.
Exemplo:

curl -X POST -H 'Authorization: Bearer $ACCESS_TOKEN' -H "Content-Type: application/json" -d
'{
   	"site_id":"MLA"
}'
https://api.mercadolibre.com/users/test_user
Resposta:

{
	"id":120506781,
    "nickname":"TEST0548",
    "password":"qatest328",
    "site_status":"active"
}
Excelente! Você receberá o User_id, apelido, senha e status atual de seu novo usuário de teste na resposta.

Nota:
Após a criação do usuário de teste, recomendamos que você salve os dados e as credenciais.

Considerações
Você pode criar até 10 usuários de teste com sua conta de Mercado Livre. (quando o usuário de teste é criado, as credenciais devem ser salvas, não temos um recurso que mostre os usuários de teste criados e suas credenciais.)
Os usuários de teste não estarão ativos durante muito tempo, mas uma vez que expirarem, você poderá criar novos.
Os anúncios devem ter o título “Item de Teste – Por favor, NÃO OFERTAR!”.
Na medida do possível, publique na categoria “Outros”.
Não se deve publicar em “gold” nem “gold_premium” para que não apareça na nossa página de início.
Os usuários de testes podem simular operações apenas com anúncios de outros usuários de teste: só podem comprar, vender, fazer perguntas, etc., em anúncios de teste, criados por contas de teste.
Os usuários de testes sem atividade (comprar, solicitar, publicar etc.) por 60 dias são removidos imediatamente.
Esses itens são removidos periodicamente.
Se você perder a senha da conta de teste, não é possível recuperar, sendo assim é necessário criar uma nova conta.
Caso seu usuário de teste seja bloqueado indevidamente, carregue os dados do seu usuário de teste neste suporte.
O código de validação de e-mail para usuários de teste será igual aos últimos dígitos do ID do usuário, o tamanho do código pode ser de 4 ou 6 dígitos dependendo do caso. Por exemplo, se fosse solicitado um código de 6 dígitos para o usuário ID 653764425, o código de verificação seria 764425.

Comprar e vender entre usuários de teste
Lembre-se de que os testes na plataforma e todas as transações devem ser feitas com usuários de teste. Além disso, as contas pessoais não devem conter anúncios. Para simular compras entre usuários de teste você deve utilizar cartões de teste. Lembre-se de que os testes na plataforma e todas as transações devem ser feitas entre usuários de teste. Além disso, as contas pessoais não devem conter anúncios para este fim.

Notas:
- Os dados que você deve carregar são fictícios e que por segurança não adicionamos os nomes dos bancos nos cartões disponíveis para realizar testes.

- Para testar diferentes resultados de pagamento, complete o status de pagamento pretendido no primeiro e último nome do titular do cartão no checkout. Por exemplo, se você quiser que o pagamento seja aprovado, você ingressaria "APRO APRO".
Validador de publicações
Como sabemos, para realizar uma publicação, às vezes é preciso fazer mais de uma tentativa, portanto, estamos oferecendo a possibilidade de consultar se a publicação ficou exatamente como você queria antes de publicá-la. A API Produtos oferece um serviço de validação para controlar todos os detalhes de sua publicação antes que ela esteja publicada. Use-o para praticar até conseguir!


Exemplos de validação
Agora vamos ver um exemplo de como ele funciona. Vamos supor que você enviou esse JSON.


Exemplo:

{
"seller_id":,
"id",
"price":"p",
"seller_contact":null,
"pictures": [[1,2,3]] 
}
Para esta url:

curl -X POST -H 'Authorization: Bearer $ACCESS_TOKEN' https://api.mercadolibre.com/items/validate
Como resultado, você receberá uma descrição exata das melhorias que deverá implantar em seu JSON para que a publicação de seu anúncio seja bem-sucedida:

{ "message":"body.invalid_field_types", "error":"[invalid property type: [price]
    expected Number but was String value: p, invalid property type: [seller_contact]
    expected Map but was Null value: null, invalid property type: [pictures[0]]
    expected Map but was JSONArray value: [1, 2, 3], invalid property type:
    [seller_id] expected Number but was String value: id]", "status":400, "cause":[
    ] }
Validação de seu produto
curl -X POST -H 'Authorization: Bearer $ACCESS_TOKEN' -H "Content-Type: application/json" -d'{
  "title":"Teacup",
  "category_id":"MLA1902",
  "price":10,
  "currency_id":"ARS",
  "available_quantity":1,
  "buying_mode":"buy_it_now",
  "listing_type_id":"bronze",
  "condition":"new",
  "description": "Item:, Teacup Model: 1. Size: 5cm. Color: White. New in Box",
  "video_id": "YOUTUBE_ID_HERE",
  "pictures":[
    {"source":"http://upload.wikimedia.org/wikipedia/commons/e/e9/Tea_Cup.jpg"}
  ]
}' https://api.mercadolibre.com/items/validate
Validação de um produto com variações
curl -X POST -H 'Authorization: Bearer $ACCESS_TOKEN' -H "Content-Type: application/json" -d '{  
   "title":"Short",
   "category_id":"MLA126455",
   "price":10,
   "currency_id":"ARS",
   "buying_mode":"buy_it_now",
   "listing_type_id":"bronze",
   "condition":"new",
   "description": "Short with variations", 
   "variations":[
      {
      "attribute_combinations":[
        {
          "id":"93000",
          "value_id":"101993"
        },
        {
          "id":"83000",
          "value_id":"91993"
        }
      ],
      "available_quantity":1,
      "price":10,
      "picture_ids":[
          "http://bttpadel.es/image/cache/data/ARTICULOS/PROVEEDORES/BTTPADEL/BERMUDA%20ROJA-240x240.jpg"
      ]
      },
      {
      "attribute_combinations":[
        {
          "id":"93000",
          "value_id":"101995"
        },
                {
          "id":"83000",
          "value_id":"92013"
        }
      ],
      "available_quantity":1,
      "price":10,
      "picture_ids":[
          "http://www.forumsport.com/img/productos/299x299/381606.jpg"
      ]
      }
   ]
}' https://api.mercadolibre.com/items/validate
Validação de seu produto imóvel
curl -X POST -H 'Authorization: Bearer $ACCESS_TOKEN' -H "Content-Type: application/json" -d' { 
  "site_id": "MLA",
  "title": "Propiedad en Alquiler, Item de Testeo, Por favor, no ofertar",
  "category_id": "MLA52745",
  "price": 5000,
  "currency_id": "ARS",
  "available_quantity": 1,
  "buying_mode": "classified",
  "listing_type_id": "silver",
  "condition": "not_specified",
  "pictures": [
    {
      "source":"http://farm3.staticflickr.com/2417/2176897085_946b7b66b8_b.jpg"
    },
    {
      "source":"http://farm2.staticflickr.com/1056/628680053_3b7c315548_b.jpg"
    }
  ],
  "seller_contact": {
    "contact": "Pepe",
    "other_info": "Additional contact info",
    "area_code": "011",
    "phone": "4444-5555",
    "area_code2": "",
    "phone2": "",
    "email": "contact-email@somedomain.com",
    "webmail": ""
  },
  "location": {
    "address_line": "My property address 1234",
    "zip_code": "1111",
    "neighborhood": {
      "id": "TUxBQlBBUzgyNjBa"
    },
    "latitude": -34.48755,
    "longitude": -58.56987,
  },  
  "attributes": [
    {
      "id": "MLA50547-AMBQTY",
      "value_id": "MLA50547-AMBQTY-1"
    },
    {
      "id": "MLA50547-ANTIG",
      "value_id": "MLA50547-ANTIG-A_ESTRENAR"
    },
    {
      "id": "MLA50547-MTRS",
      "value_name": "500"
    },
    {
      "id": "MLA50547-SUPTOTMX",
      "value_name": "2000"
    },
    {
      "id": "MLA50547-BATHQTY",
      "value_id": "MLA50547-BATHQTY-1"
    },
    {
      "id": "MLA50547-DORMQTYB",
      "value_id": "MLA50547-DORMQTYB-3"
    },
    {
      "id": "MLA50547-EDIFIC",
      "value_id": "MLA50547-EDIFIC-CHALET"
    }
  ],
   "description" : "This is the real estate property description."
}' https://api.mercadolibre.com/items/validate
Referência de códigos de erro
Caso a publicação seja correta, você receberá uma mensagem “HTTP/1.1 204 No Content” da API de Produtos. Aclaração: Para ver a mensagem “HTTP/1.1 204 No Content” na tela, adicione o parâmetro -i ao comando curl.


Considerações
Apesar de o processo de validação não ser obrigatório, ele pode ser útil no momento de testar seu aplicativo: Lembre-se de que não existe sandbox nem ambiente de pré-produção, por isso, todos os produtos publicados durante a fase de teste ficarão visíveis para todos os usuários que estiverem navegando em nosso Marketplace. Consulte o tutorial Testes para saber sobre as particularidades e práticas recomendadas no momento de iniciar o processo.


Seguinte: Consulta API Docs.
Boas práticas para uso da plataforma
Considere que ao ser uma aplicação integradas com a API de Meli, as ações têm um impacto grande quando se executam ações massivas nas contas dos vendedores, assim, o mal uso da plataforma pode gerar sanções em suas contas.
Siga as recomendações a seguir para evitar penalizações nas contas de vendedores.

Moderações ou suspensões de contas por:
Envio de mensagens automáticas
Use sempre os motivos para se comunicar, exclusivamente nos cenários especificados.
Não está permitido enviar mensagens automáticas (repetitivas ou templates) de nenhum tipo, pois serão bloqueadas pelo Mercado Livre.
Evite o envio de mensagens desnecessárias como "recebemos sua compra"ou atualizações de status de envio, já que a partir de nossa integração é possível atualizar o estado para pedidos ME1, enquanto para ME2 a atualização é feita pelo Meli e informada diretamente ao comprador.
As mensagens repetitivas ou desnecessárias geram spam e uma má experiência ao comprador. Por este motivo, informamos aos nossos vendedores como e quando enviar uma mensagem pós-venda e assim entender estrategicamente em quais momentos contatar o comprador para ganhar tempo e esforço.

Modificação em template de etiquetas
Não está permitido qualquer alteração no template das etiquetas geradas pelo Mercado Livre.
Clonagem de publicação
Não recomendamos clonar as publicações. Este cenário será moderado pelas políticas de publicação de MeLi. Conheça mais sobre Anúncios duplicados.
Também não recomendamos clonar imagens Conheça como tirar boas fotos.
Considerar o uso das funcionalidades para os tipos de produtos
Itens elegíveis para catálogo sempre devem ser publicado em catálogo ou por optin.
Itens de autopeças (peças de reposição) sempre devem ter as compatibilidades associadas e informar as exceções correspondentes.
Itens de moda sempre devem ser publicados com a tabela de medidas associada.

Sendo uma API aberta de Mercado Livre, você deve considerar algumas técnicas importantes:


Web Crawler:
- Não fazer web crawling, e sim sempre trabalhar com la API de MeLi.
- É recomendável limitar os IPs de seu ambiente para utilizar o access token de sua aplicação.
- Considere que existem limites de requisições em alguns endpoints, ou seja, deverá identificar o erro 429 recebido em sua integração e diminuir e/ou melhorar a distribuição de requisições realizadas ao longo do tempo.
Considerações sobre design
Ao começar a trabalhar com nossa API, você deve levar em consideração alguns conceitos básicos.


Formato JSON
O formato JSON é um padrão aberto baseado em texto leve projetado para a troca de dados legíveis. Você pode ler esses tipos de mensagens através de um navegador, ferramentas específicas (por exemplo, Postman) ou de qualquer desenvolvimento que consuma a API do Mercado Livre.


Uso de JSONP
Se você incluir um parâmetro callback, a API responderá com JSONP. O valor deste parâmetro será usado como a função de callback.
Exemplo:

curl -X GET https://api.mercadolibre.com/currencies/ARS
Resposta:

{
  "id": "ARS",
  "description": "Peso argentino",
  "symbol": "$",
  "decimal_places": 2,
}

Para uma resposta JSONP, adicione um parâmetro de retorno como o seguinte:

curl -X GET https://api.mercadolibre.com/currencies/ARS?callback=foo
Resposta:

foo
( [ 200, {
  "Content-Type": ["text/javascript;charset=UTF-8"],
  "Cache-Control": ["max-age=3600,stale-while-revalidate=1800, stale-if-error=7200"]
}, {
  "id": "ARS",
  "symbol": "$",
  "description": "Peso argentino",
  "decimal_places": 2
} ] )
Como vemos, a resposta é um conjunto de três valores:

Código de status https
Cabeçalhos de resposta https
Corpo da resposta
Todas as respostas JSONP sempre serão 200 OK. O propósito disso é que você tenha a possibilidade de lidar com respostas 30x, 40x e 50x.


Tratamento de erros
O formato padrão de um erro é o seguinte:

{
  "message": "human readable text",
  "error": "machine_readable_error_code",
  "status": 400,
  "cause": [ ],
}
Redução de respostas
Para ter respostas mais curtas, com uma quantidade menor de dados, você pode acrescentar o parâmetro atributos com uma vírgula separando a lista de campos que devem ser incluídos na resposta. Todos os campos restantes da resposta original serão ignorados. Isso só é aceito para as respostas do conjunto.

curl -X GET https://api.mercadolibre.com/currencies?attributes=id
[
  {
  "id": "BRL"
  },
  {
  "id": "UYU"
  },
  {
  "id": "CLP"
  },
  ...
]
Utilização de OPTIONS
A API entregará documentação no formato JSON usando OPTIONS.

curl -X OPTIONS https://api.mercadolibre.com/currencies
{
  "name":"Monedas",
    "description":"Devuelve información correspondiente al ISO de las monedas que se usan en MercadoLibre.",
  "attributes": {
     "id":"ID de la moneda (Código ISO)",
        "description":"Denominación oficial de la moneda",
      "symbol":"Símbolo ISO para representar la moneda",
        "decimal_places":"Número de decimales manejados con la moneda"
  },
  "methods": [
     {
            "method":"GET",
            "example":"/currencies/",
            "description":"Devuelve el listado con todas las monedas."
      },
      {
            "method":"GET",
            "example":"/currencies/:id",
          "description":"Devuelve información con respecto a una moneda específica."
      }
  ],
  "related_resources":[],
  "connections": {
        "id":"/currencies/:id"
  }
}
Paginação de resultados
Você pode definir o tamanho da página da lista de resultados. Existem 2 parâmetros: limit e offset. Ambos os parâmetros definem o tamanho do bloco dos resultados. Este artigo é baseado no exemplo de pesquisa, mas você pode usar a paginação em cada recurso que é apresentado nas informações de resposta "paginação", conforme mostrado abaixo:

.....
  "paging": {
  "total": 285,
  "offset": 0,
  "limit": 50,
  }
  .....


Valores padrão
Os valores padrão são offset=0 e limit=50.

curl https://api.mercadolibre.com/sites/MLA/search?q=ipod nano
Na seção de paginação da resposta JSON, é possível ver o número total de itens que correspondem à pesquisa e o valor do offset com o limit padrão aplicado.

.....
  "paging": {
  "total": 285,
  "offset": 0,
  "limit": 50,
  }
  .....
Limit
Para reduzir o tamanho da página, você pode alterar o parâmetro limite. Por exemplo, se você estiver interessado em recuperar apenas os 3 primeiros itens:

curl -X GET https://api.mercadolibre.com/sites/MLA/search?q=ipod nano&limit=3
Esta ação recupera dados JSON com um conjunto de 3 artigos, conforme ilustrado abaixo:

{
  "site_id": "MLA",
  "query": "ipod nano",
  "paging": {
  "total": 284,
  "offset": 0,
  "limit": 3,
  },
  "results": [
  {...},
  {...},
  {...},
  ],
  "sort": {...},
  "available_sorts": [...],
  "filters": [...],
  "available_filters": [...],
}
Offset
Usando o atributo deslocamento, você pode mover o limite inferior do bloco de resultados. Por exemplo, se você estiver interessado em recuperar os 50 artigos que seguem a resposta padrão:

curl https://api.mercadolibre.com/sites/MLA/search?q=ipod nano&offset=50
{
  "site_id": "MLA",
  "query": "ipod nano",
  "paging": {
  "total": 285,
  "offset": 50,
  "limit": 50,
  },
  "results": [...],
  "sort": {...},
  "available_sorts": [...],
  "filters": [...],
  "available_filters": [...],
}
Esta resposta recupera 50 artigos dos primeiros cinquenta.


Definir um intervalo de resultados
É possível combinar os dois parâmetros. Você pode recuperar itens do terceiro ao sexto no resultado da pesquisa original:

curl https://api.mercadolibre.com/sites/MLA/search?q=ipod nano&offset=3&limit=3
Esta ação recupera o dado JSON com um conjunto de 5 artigos, conforme abaixo:

{
  "site_id": "MLA",
  "query": "ipod nano",
  "paging": {
  "total": 285,
  "offset": 3,
  "limit": 3,
  },
  "results": [
  {...},
  {...},
  {...},
  ],
  "sort": {...},
  "available_sorts": [...],
  "filters": [...],
  "available_filters": [...],
}
Seguinte: Minha primeira aplicação.
Gerenciar IPs de um aplicativo
Importante:
Essa funcionalidade é exclusiva para integradores withe listeado
Esta documentação tem como objetivo mostrar a funcionalidade disponível no devcenter para gerenciamento e configuração de intervalos de IP que serão permitidos para o consumo de nossas APIs. Descrevendo os possíveis fluxos que um usuário pode executar a partir dessa nova tela.


Gerenciar intervalos de IP
Para entrar nos aplicativos você deve estar logado no devcenter e acessar seu perfil. Para cada aplicativo integrado, você encontrará um menu despregavel, onde será exibida a opção Gerenciar intervalos de IP.




Nota:
Se a Gerenciar intervalos de IPnão estiver listada, é porque o aplicativo não está habilitado para gerenciar IPs.

Lista de intervalos
Na parte inferior da tela, é mostrada uma lista dos IPs configurados no aplicativo. Na barra de busca, você pode digitar o intervalo que deseja encontrar mais rapidamente: ⁣




Adicionar novo IP
O número de IPs que foram adicionados ao aplicativo e o número de IPs disponíveis são exibidos no lado direito da tela. Se você ainda tiver intervalos disponíveis, a seção para adicionar um novo IP será habilitada.

Existe a possibilidade de adicionar novos IPs de duas formas:

Adicionando o IP individualmente.
Massivamente, carregando um arquivo com extensão .csv com a lista de IPs a serem adicionados.



Considerações
Somente IPs v4 ou v6 no formato CIDR (Classles inter-domain routing) são permitidos, um erro é exibido quando o formato não está correto:


A validação do número de intervalos de IP disponíveis é realizada tanto no processo individual quanto no processo massivo.


Adicionando o IP individualmente
É necessário digitar o novo IP que deseja adicionar, caso não tenha nenhum erro de formato pode clicar no botão Adicionar.


Será exibida uma mensagem de erro ou êxito, dependendo do resultado do processo:





Carga massiva de IPs
Para adicionar vários intervalos de IP em simultâneo, é necessário clicar no botão Anexar .CSV. Será aberto um modal onde o usuário vai carregar o arquivo:



Considerações
O arquivo deve ter uma extensão .csv. Um erro será exibido se esta condição não for atendida.


O arquivo não deve conter cabeçalhos.
Cada intervalo de IP deve ser separado por uma vírgula (,).
Cada IP deve ter o formato correspondente ou não será considerado na carga massiva.

Exemplo de arquivo a carregar:

Nome: test.csv

Conteúdo:



Após anexar o arquivo, clique no botão Archivo CSV anexado.



O sistema exibirá uma mensagem de êxito ou erro, dependendo do resultado do processo.

Mensagem de êxito: exibida quando todos os intervalos de IP no arquivo foram carregados com êxito.



Mensagem de erro: é mostrada quando a adição de todos ou algum intervalos falhou. Ou devido ao formato de registro ou erro de sobreposição de intervalos.


O modal exibirá o número de intervalos que foram adicionados com êxito e o número de intervalos que falharam.



Tem a opção de clicar no botão Conferir resultados onde será baixado um arquivo com extensão .csv com as informações dos registros que não puderam ser adicionados e uma descrição do erro. Isso é para que o usuário possa ver os erros, corrigi-los e tentar novamente realizar a carga massiva com os intervalos que faltaram.



Eliminar intervalos de IPs
Para excluir um intervalo, só precisa clicar na opção Selecionar todos se desejar excluir todos os intervalos parametrizados ou selecionar apenas aqueles que deseja excluir.


Em seguida, clique no botão Apagar.



Será exibido um modal como um aviso para o usuário possa confirmar a execução do processo.



Finalmente, uma mensagem de erro ou êxito será exibida dependendo do resultado da eliminação dos intervalos correspondentes.
Erro 403
Para o tratamento de erros 403 - Forbidden, é necessário identificar sua causa e possível solução. Este erro está comumente relacionado a problemas de permissões e restrições de acesso tais como: uso de access token de outro usuário, usuários inativos, solicitações provenientes de um IP não permitido, scopes inabilitados, aplicação bloqueada ou desabilitada. Além disso, pode ser causado pela falta de completude em validações dos usuários.

Exemplo de erro:

    {
        "status": 403,
        "error": "Invalid scopes",
        "code": "FORBIDDEN"
    }
Se você receber a mensagem: "o acesso ao recurso solicitado é proibido," isso indica que você está tentando acessar informações que não correspondem ao token de acesso fornecido ou que você não possui as permissões necessárias para executar a solicitação.

    {
        "status": 403,
        "error": "access_denied",
        "message": "access to the requested resource is forbidden",
        "code": "FORBIDDEN"
    }

Validações
Aplicação bloqueada ou desabilitada: garanta que a sua aplicação que realiza a solicitação não esteja bloqueada ou desabilitada por descumprimento dos nossos Termos e Condições. Ver dados privados da sua aplicação.
Permissões insuficientes: o usuário ou a aplicação não possuem as permissões necessárias para acessar o recurso solicitado.
Usuários inativos: a solicitação pode estar vindo de um usuário que está inativo ou foi suspenso pelo Mercado Livre. Verificar o estado de um usuário.
IPs bloqueados: a solicitação está vindo de um endereço IP que não está na lista permitida. Saiba como gerenciar IPs de uma aplicação.
Validar os scopes da aplicação: garanta que os scopes necessários para a operação estejam corretamente configurados no DevCenter.
Validar que o Access token seja o do owner da informação: asegure o uso de access tokens individuais garantindo o uso correto e seguro.
Validar dados dos usuários: o usuário deve ter concluído o processo de validação de dados.
O tratamento adequado do erro 403 é crucial para garantir que apenas os usuários e aplicações autorizados possam acessar os recursos.
