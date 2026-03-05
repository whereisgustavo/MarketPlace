from shared.utilities import normalizar_nome
from servidor.excepcoes import ExcepcaoSupermercadoCategoriaJaExistente
from servidor.excepcoes import ExcepcaoSupermercadoCategoriaNaoExistente
from servidor.excepcoes import ExcepcaoSupermercadoCategoriaTemProduto
from servidor.categoria import Categoria


class Loja:

    def __init__(self):
        self._categorias = {}

        # adicionado
        # ainda n há produtos, mas para usar o REMOVE_CATEGORIA temos de saber se há produtos
        # fica vazio, conta 0   
        self._produtos = {}

    def reset(): 
        Categoria._contador_global = 1
        # TODO: MUITO IMPORTANTE Completar esta funcao para Testes Unitários puderem executar sem problemas

    # -----------------------------
    # Categorias 
    # -----------------------------
    def criar_categoria(self, nome):
        nome = normalizar_nome(nome)
        if self.obter_id_categoria(nome) is not None:
            raise ExcepcaoSupermercadoCategoriaJaExistente(nome)
        categoria = Categoria(nome)
        self._categorias[categoria.id] = categoria
        return categoria
    
    def obter_id_categoria(self, nome): 
        for c in self._categorias.values(): 
            if nome == c.nome: 
                return c.id
        return None
    
    # adicionado
    # metodo apenas usado em Loja 
    def _numero_produtos_categoria(self, id_categoria):
        total = 0
        for p in self._produtos.values():  # p devera ter p.id_categoria
            if hasattr(p, "id_categoria") and p.id_categoria == id_categoria:
                total += 1
        return total
    
    # adicionado
    def listar_categorias(self):
        if len(self._categorias) == 0:
            return "NÃO HÁ CATEGORIAS REGISTADAS."
        
        # total de produtos, nº total de produtos que estão registados
        prod_total = 0
        if hasattr(self, "_produtos"):
            prod_total = len(self._produtos)

        linhas = []
        linhas.append(f"CATEGORIAS REGISTADAS: {len(self._categorias)}")
        linhas.append(f"PRODUTOS REGISTADOS: {prod_total}")

        # ordena por id_categoria
        for id_categoria in sorted(self._categorias.keys()):
            categoria = self._categorias[id_categoria]
            n_prod_categoria = self._numero_produtos_categoria(id_categoria)
            linhas.append(f"{categoria.id} - {categoria.nome} ({n_prod_categoria} produtos)")

        return "\n".join(linhas)
    
    # adicionado
    def remover_categoria(self, nome):
        nome_normalizado = normalizar_nome(nome)
        id_categoria = self.obter_id_categoria(nome_normalizado)

        if id_categoria is None:
            raise ExcepcaoSupermercadoCategoriaNaoExistente(nome_normalizado)
        
        # se tem produtos, não pode remover (regra dita pela professora)
        if self._numero_produtos_categoria(id_categoria) > 0:
            raise ExcepcaoSupermercadoCategoriaTemProduto(nome_normalizado)
        
        categoria = self._categorias[id_categoria]
        del self._categorias[id_categoria]
        return categoria

    