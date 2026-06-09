import hashlib
import hmac # compare_digest가 타이밍 공격을 줄여준다???
import secrets


HASH_ALGORITHM = "sha256"
HASH_ITERATIONS = 600_000 # (속도 : 무차별 대입 공격 대응) = 비례
SALT_BYTES = 16 # salt 길이


def hash_password(password: str) -> str:
    salt = secrets.token_hex(SALT_BYTES) # 비밀번호마다 다른 salt 생성
    password_hash = hashlib.pbkdf2_hmac( # password + salt as PBKDF2.
        HASH_ALGORITHM,
        password.encode("utf-8"),
        salt.encode("utf-8"),
        HASH_ITERATIONS,
    ).hex() # bytes to hex string

    return f"pbkdf2_{HASH_ALGORITHM}${HASH_ITERATIONS}${salt}${password_hash}"


def verify_password(password: str, stored_password: str) -> bool:
    try:
        # DB에 저장된 문자열을 다시 split 함
        algorithm, iterations, salt, expected_hash = stored_password.split("$")

        # 문자열에서 hash값만 parsing
        hash_algorithm = algorithm.replace("pbkdf2_", "")

        # salt와 iterations로 암호화
        actual_hash = hashlib.pbkdf2_hmac(
            hash_algorithm,
            password.encode("utf-8"),
            salt.encode("utf-8"),
            int(iterations),
        ).hex()
    except ValueError:
        return False

    return hmac.compare_digest(actual_hash, expected_hash) # 해시 비교
