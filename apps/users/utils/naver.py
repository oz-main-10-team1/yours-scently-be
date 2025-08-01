import logging
import os
from typing import Any, Dict, Optional, cast

import logger
import requests


# 토큰 발급
def get_naver_access_token(code: str, redirect_uri: str, state: Optional[str] = None) -> Optional[str]:

    client_id = os.getenv("NAVER_CLIENT_ID")
    client_secret = os.getenv("NAVER_CLIENT_SECRET")
    # redirect_uri = os.getenv("NAVER_REDIRECT_URI")

    params = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "redirect_uri": redirect_uri,
    }
    if state:
        params["state"] = state

    try:
        response = requests.get("https://nid.naver.com/oauth2.0/token", params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("access_token")
    except requests.RequestException as e:
        logger.warning(f"[NAVER] Failed to get access token: {e}")
        if response is not None:
            logger.debug(f"[NAVER] Status: {response.status_code}, Body: {response.text}")
        return None


def verify_naver_token(access_token: str) -> Optional[Dict[str, Optional[str]]]:
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = requests.get("https://openapi.naver.com/v1/nid/me", headers=headers)
        response.raise_for_status()
        data = response.json()

        if data.get("resultcode") != "00":
            logger.warning(f"[NAVER] Invalid result code from user info: {data}")
            return None

        return data.get("response", {})
    except requests.RequestException as e:
        logger.warning(f"[NAVER] Failed to verify token: {e}")
        if response is not None:
            logger.debug(f"[NAVER] Status: {response.status_code}, Body: {response.text}")
        return None
