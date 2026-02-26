#!/usr/bin/env python3
"""
baixar_instagram_v2.py
Baixa imagens (melhor resolução) de um perfil público/permitido com tolerância a rate-limit.

Uso (exemplos):
  python baixar_instagram_v2.py marcelo.santos.77
  python baixar_instagram_v2.py marcelo.santos.77 --login MEUUSER
  python main.py leonardossil --sessionid "1999f5e3ec7-75a026"
  python baixar_instagram_v2.py marcelo.santos.77 --session-file .session-MEUUSER.json
  python baixar_instagram_v2.py marcelo.santos.77 --fast-update

Dependência:
  pip install instaloader
"""

import argparse
import getpass
import json
import os
import re
import time
from typing import Optional

import instaloader
from instaloader.exceptions import (
    ConnectionException,
    QueryReturnedBadRequestException,
    QueryReturnedNotFoundException,
    QueryReturnedForbiddenException,
    BadCredentialsException,
    TwoFactorAuthRequiredException,
    ProfileNotExistsException,
)

PLEASE_WAIT_PAT = re.compile(r"please wait a few minutes", re.IGNORECASE)


def save_session(L: instaloader.Instaloader, path: str):
    """Salva cookies/sessão em JSON simples (portável)."""
    data = L.context._session.cookies.get_dict()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)
    print(f"[+] Sessão salva em: {path}")


def load_session(L: instaloader.Instaloader, path: str):
    """Carrega cookies/sessão de JSON simples."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    for k, v in data.items():
        L.context._session.cookies.set(k, v)
    # testa
    username = L.test_login()
    print(f"[+] Sessão carregada. Logado como: {username}" if username else "[!] Sessão não autenticada.")


def apply_sessionid(L: instaloader.Instaloader, sessionid: str):
    """Injeta diretamente o cookie sessionid (método alternativo sem senha)."""
    L.context._session.cookies.set("sessionid", sessionid, domain=".instagram.com", path="/")
    username = L.test_login()
    print(f"[+] sessionid aplicado. Logado como: {username}" if username else "[!] sessionid inválido ou expirado.")


def create_loader(dest_dir: Optional[str]) -> instaloader.Instaloader:
    return instaloader.Instaloader(
        dirname_pattern=dest_dir or "{target}",
        download_videos=False,            # apenas imagens
        download_video_thumbnails=False,
        save_metadata=True,
        post_metadata_txt_pattern=None,
        compress_json=False,
        max_connection_attempts=3,
        # quiet=True,
    )


def polite_sleep(seconds: int):
    """Dormir exibindo um contador regressivo simpático."""
    for s in range(seconds, 0, -1):
        print(f"   aguardando {s:>3}s...", end="\r")
        time.sleep(1)
    print(" " * 30, end="\r")


def should_backoff(exc: Exception) -> bool:
    text = str(exc)
    return (
        isinstance(exc, (ConnectionException, QueryReturnedBadRequestException, QueryReturnedForbiddenException))
        or PLEASE_WAIT_PAT.search(text) is not None
        or "429" in text
        or "rate limit" in text.lower()
    )


def download_profile_images(
    username: str,
    dest_dir: Optional[str],
    login_user: Optional[str],
    use_fast_update: bool,
    session_file: Optional[str],
    sessionid: Optional[str],
):
    L = create_loader(dest_dir)

    # Autenticação (prioridade: session-file > sessionid > login)
    if session_file and os.path.exists(session_file):
        load_session(L, session_file)
    elif sessionid:
        apply_sessionid(L, sessionid)
    elif login_user:
        try:
            pwd = getpass.getpass(f"Senha de {login_user}: ")
            L.login(login_user, pwd)
            print(f"[+] Logado como {login_user}")
            # Salva sessão para reutilizar depois
            session_path = f".session-{login_user}.json"
            save_session(L, session_path)
        except TwoFactorAuthRequiredException:
            code = input("Código 2FA: ").strip()
            L.two_factor_login(code)
            print(f"[+] 2FA ok. Logado como {login_user}")
            session_path = f".session-{login_user}.json"
            save_session(L, session_path)
        except BadCredentialsException:
            print("[!] Credenciais inválidas.")
        except Exception as e:
            print("[!] Falha no login:", e)

    # Backoff progressivo (60s → 2m → 5m → 10m → 20m)
    backoffs = [60, 120, 300, 600, 1200]
    bo_idx = 0

    # Fast-update reduz requisições (baixa só novos)
    if use_fast_update:
        L.context.log("[i] fast-update habilitado (menos chamadas).")

    try:
        profile = instaloader.Profile.from_username(L.context, username)
    except ProfileNotExistsException:
        print(f"[ERROR] Perfil '{username}' não existe.")
        return
    except Exception as e:
        print("[ERROR] Não foi possível obter informações do perfil:", e)
        return

    print(f"[+] Iniciando download de posts do perfil: {profile.username}")
    print(f"    total de posts estimado: {profile.mediacount}")
    print(f"    perfil público: {not profile.is_private}")

    target = profile.username
    os.makedirs(dest_dir or target, exist_ok=True)

    processed = 0
    while True:
        try:
            # Iterar posts — se falhar por rate-limit, cai no except e aplica backoff
            count_before = processed
            for post in profile.get_posts():
                if use_fast_update and post.is_pinned:
                    # posts fixados às vezes já foram baixados; seguimos o fluxo normal
                    pass

                if post.is_video:
                    print(f" - pulando vídeo: {post.shortcode}")
                    continue

                L.download_post(post, target=target)
                processed += 1
                print(f" - baixado post {post.shortcode} (#{processed})")

            # Se percorreu tudo sem erro, encerra
            break

        except (QueryReturnedNotFoundException,) as e:
            print("[!] Conteúdo não encontrado/alterado:", e)
            break
        except Exception as e:
            # Detecta rate-limit explícito/implícito
            if should_backoff(e):
                wait_s = backoffs[min(bo_idx, len(backoffs) - 1)]
                msg = str(e)
                print(f"[!] Rate-limit ou bloqueio temporário detectado: {msg[:120]}...")
                print(f"[i] Aguardando {wait_s//60} min antes de retomar (backoff nível {bo_idx+1}).")
                polite_sleep(wait_s)
                bo_idx += 1
                # Se nada foi baixado nessa rodada, tente outra; caso contrário, continua
                continue
            else:
                print("[!] Erro não tratável (parando):", e)
                break

        finally:
            # Se não baixou nada na rodada atual, evita loop infinito
            if processed == count_before and bo_idx >= len(backoffs):
                print("[i] Sem progresso após múltiplos backoffs. Encerrando para evitar bloqueio.")
                break

    print(f"[+] Finalizado. Posts com imagens processados: {processed}")
    print(f"[+] Arquivos salvos em: ./{dest_dir or target}/")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("username", help="username do Instagram (ex.: marcelo.santos.77)")
    ap.add_argument("--dest", help="pasta destino (default: ./<username>)")
    ap.add_argument("--login", help="fazer login com este usuário (salva sessão)")
    ap.add_argument("--session-file", help="carregar sessão de arquivo JSON salvo")
    ap.add_argument("--sessionid", help="usar cookie 'sessionid' diretamente (alternativa ao login)")
    ap.add_argument("--fast-update", action="store_true", help="baixar só novos; reduz chamadas")
    args = ap.parse_args()

    download_profile_images(
        username=args.username,
        dest_dir=args.dest,
        login_user=args.login,
        use_fast_update=args.fast_update,
        session_file=args.session_file,
        sessionid=args.sessionid,
    )


if __name__ == "__main__":
    main()
