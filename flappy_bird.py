import os
import random

import pygame

TELA_LARGURA = 500
TELA_ALTURA = 800
FPS = 30

PASTA_IMAGENS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'imgs')


def carregar_imagem(nome):
    return pygame.transform.scale2x(pygame.image.load(os.path.join(PASTA_IMAGENS, nome)))


IMAGEM_CANO = carregar_imagem('pipe.png')
IMAGEM_CHAO = carregar_imagem('base.png')
IMAGEM_BACKGROUND = carregar_imagem('bg.png')
IMAGENS_PASSARO = [
    carregar_imagem('bird1.png'),
    carregar_imagem('bird2.png'),
    carregar_imagem('bird3.png'),
]

pygame.font.init()
FONTE_PONTOS = pygame.font.SysFont('arial', 50)
FONTE_AVISO = pygame.font.SysFont('arial', 28)


class Passaro:
    IMGS = IMAGENS_PASSARO
    # animação de rotação
    ROTACAO_MAXIMA = 25
    VELOCIDADE_ROTACAO = 20
    TEMPO_ANIMACAO = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angulo = 0
        self.velocidade = 0
        self.altura = self.y
        self.tempo = 0
        self.contagem_imagem = 0
        self.imagem = self.IMGS[0]

    def pular(self):
        self.velocidade = -10.5
        self.tempo = 0
        self.altura = self.y

    def mover(self):
        # calcular o deslocamento
        self.tempo += 1
        deslocamento = 1.5 * (self.tempo ** 2) + self.velocidade * self.tempo

        # restringir o deslocamento
        if deslocamento > 16:
            deslocamento = 16
        elif deslocamento < 0:
            deslocamento -= 2

        self.y += deslocamento

        # o ângulo do pássaro
        if deslocamento < 0 or self.y < (self.altura + 50):
            if self.angulo < self.ROTACAO_MAXIMA:
                self.angulo = self.ROTACAO_MAXIMA
        else:
            if self.angulo > -90:
                self.angulo -= self.VELOCIDADE_ROTACAO

    def desenhar(self, tela):
        # definir qual imagem do pássaro vai usar
        self.contagem_imagem += 1

        if self.contagem_imagem < self.TEMPO_ANIMACAO:
            self.imagem = self.IMGS[0]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO * 2:
            self.imagem = self.IMGS[1]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO * 3:
            self.imagem = self.IMGS[2]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO * 4:
            self.imagem = self.IMGS[1]
        else:
            self.imagem = self.IMGS[0]
            self.contagem_imagem = 0

        # se o pássaro estiver caindo ele não bate asa
        if self.angulo <= -80:
            self.imagem = self.IMGS[1]
            self.contagem_imagem = self.TEMPO_ANIMACAO * 2

        # desenhar a imagem
        imagem_rotacionada = pygame.transform.rotate(self.imagem, self.angulo)
        pos_centro_imagem = self.imagem.get_rect(topleft=(self.x, self.y)).center
        retangulo = imagem_rotacionada.get_rect(center=pos_centro_imagem)
        tela.blit(imagem_rotacionada, retangulo.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.imagem)


class Cano:
    DISTANCIA = 200
    VELOCIDADE = 5

    def __init__(self, x):
        self.x = x
        self.altura = 0
        self.pos_topo = 0
        self.pos_base = 0
        self.CANO_TOPO = pygame.transform.flip(IMAGEM_CANO, False, True)
        self.CANO_BASE = IMAGEM_CANO
        self.passou = False
        self.definir_altura()

    def definir_altura(self):
        self.altura = random.randrange(50, 450)
        self.pos_topo = self.altura - self.CANO_TOPO.get_height()
        self.pos_base = self.altura + self.DISTANCIA

    def mover(self):
        self.x -= self.VELOCIDADE

    def desenhar(self, tela):
        tela.blit(self.CANO_TOPO, (self.x, self.pos_topo))
        tela.blit(self.CANO_BASE, (self.x, self.pos_base))

    def colidir(self, passaro):
        passaro_mask = passaro.get_mask()
        topo_mask = pygame.mask.from_surface(self.CANO_TOPO)
        base_mask = pygame.mask.from_surface(self.CANO_BASE)

        distancia_topo = (self.x - passaro.x, self.pos_topo - round(passaro.y))
        distancia_base = (self.x - passaro.x, self.pos_base - round(passaro.y))

        topo_ponto = passaro_mask.overlap(topo_mask, distancia_topo)
        base_ponto = passaro_mask.overlap(base_mask, distancia_base)

        return bool(topo_ponto or base_ponto)


class Chao:
    VELOCIDADE = 5
    LARGURA = IMAGEM_CHAO.get_width()
    IMAGEM = IMAGEM_CHAO

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.LARGURA

    def mover(self):
        self.x1 -= self.VELOCIDADE
        self.x2 -= self.VELOCIDADE

        if self.x1 + self.LARGURA < 0:
            self.x1 = self.x2 + self.LARGURA
        if self.x2 + self.LARGURA < 0:
            self.x2 = self.x1 + self.LARGURA

    def desenhar(self, tela):
        tela.blit(self.IMAGEM, (self.x1, self.y))
        tela.blit(self.IMAGEM, (self.x2, self.y))


def desenhar_texto_centralizado(tela, texto, fonte, y):
    superficie = fonte.render(texto, True, (255, 255, 255))
    tela.blit(superficie, ((TELA_LARGURA - superficie.get_width()) // 2, y))


def desenhar_tela(tela, passaros, canos, chao, pontos, recorde):
    tela.blit(IMAGEM_BACKGROUND, (0, 0))
    for passaro in passaros:
        passaro.desenhar(tela)
    for cano in canos:
        cano.desenhar(tela)

    texto = FONTE_PONTOS.render(f'Pontuação: {pontos}', True, (255, 255, 255))
    tela.blit(texto, (TELA_LARGURA - 10 - texto.get_width(), 10))
    chao.desenhar(tela)

    # fim de jogo: todos os pássaros morreram
    if not passaros:
        desenhar_texto_centralizado(tela, 'Fim de jogo!', FONTE_PONTOS, 300)
        desenhar_texto_centralizado(tela, f'Recorde: {recorde}', FONTE_AVISO, 370)
        desenhar_texto_centralizado(tela, 'Aperte ESPAÇO para jogar de novo', FONTE_AVISO, 420)

    pygame.display.update()


def novo_jogo():
    return [Passaro(230, 350)], [Cano(700)], Chao(730), 0


def main():
    pygame.display.set_caption('Flappy Bird')
    tela = pygame.display.set_mode((TELA_LARGURA, TELA_ALTURA))
    relogio = pygame.time.Clock()

    passaros, canos, chao, pontos = novo_jogo()
    recorde = 0

    rodando = True
    while rodando:
        relogio.tick(FPS)

        # interação com o usuário
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_SPACE:
                if not passaros:
                    passaros, canos, chao, pontos = novo_jogo()
                for passaro in passaros:
                    passaro.pular()

        # com o jogo encerrado, só redesenha a tela de fim de jogo
        if not passaros:
            desenhar_tela(tela, passaros, canos, chao, pontos, recorde)
            continue

        # mover as coisas
        for passaro in passaros:
            passaro.mover()
        chao.mover()

        adicionar_cano = False
        remover_canos = []
        for cano in canos:
            for passaro in passaros[:]:
                if cano.colidir(passaro):
                    passaros.remove(passaro)
                elif not cano.passou and passaro.x > cano.x:
                    cano.passou = True
                    adicionar_cano = True
            cano.mover()
            if cano.x + cano.CANO_TOPO.get_width() < 0:
                remover_canos.append(cano)

        if adicionar_cano:
            pontos += 1
            canos.append(Cano(600))

        for cano in remover_canos:
            canos.remove(cano)

        for passaro in passaros[:]:
            if (passaro.y + passaro.imagem.get_height()) > chao.y or passaro.y < 0:
                passaros.remove(passaro)

        recorde = max(recorde, pontos)
        desenhar_tela(tela, passaros, canos, chao, pontos, recorde)

    pygame.quit()


if __name__ == '__main__':
    main()
