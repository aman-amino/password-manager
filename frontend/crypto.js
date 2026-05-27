const encoder = new TextEncoder();
const decoder = new TextDecoder();

function getSubtleCrypto() {
  if (typeof window === 'undefined') {
    throw new Error("WebCrypto is only available in a browser environment.");
  }
  const cryptoObj = window.crypto || window.msCrypto;
  if (!cryptoObj) {
    throw new Error("WebCrypto API is not supported in this browser.");
  }
  if (!cryptoObj.subtle) {
    if (!window.isSecureContext) {
      throw new Error(
        "Secure Context Required: Zero-knowledge cryptographic operations require HTTPS or localhost. Please access the application via https:// or http://localhost."
      );
    }
    throw new Error("SubtleCrypto is not available in this environment.");
  }
  return cryptoObj.subtle;
}

export function toBase64(bytes) {
  let binary = "";
  bytes.forEach((b) => (binary += String.fromCharCode(b)));
  return btoa(binary);
}

export function fromBase64(b64) {
  const binary = atob(b64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i += 1) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes;
}

export function randomBytes(length) {
  const bytes = new Uint8Array(length);
  const cryptoObj = typeof window !== 'undefined' ? (window.crypto || window.msCrypto) : null;
  if (!cryptoObj) {
    throw new Error("WebCrypto API is not supported in this browser.");
  }
  cryptoObj.getRandomValues(bytes);
  return bytes;
}

export async function importPassword(password) {
  const subtle = getSubtleCrypto();
  return subtle.importKey(
    "raw",
    encoder.encode(password),
    { name: "PBKDF2" },
    false,
    ["deriveKey", "deriveBits"]
  );
}

export async function deriveRootKey(passwordKey, salt, iterations) {
  const subtle = getSubtleCrypto();
  const rootBits = await subtle.deriveBits(
    {
      name: "PBKDF2",
      salt,
      iterations,
      hash: "SHA-256",
    },
    passwordKey,
    256
  );

  return subtle.importKey(
    "raw",
    rootBits,
    { name: "HKDF" },
    false,
    ["deriveKey", "deriveBits"]
  );
}

export async function deriveSubKey(rootKey, info, usage) {
  const subtle = getSubtleCrypto();
  return subtle.deriveKey(
    {
      name: "HKDF",
      hash: "SHA-256",
      salt: new Uint8Array([]), // Salt is usually optional for HKDF if root is already strong
      info: encoder.encode(info),
    },
    rootKey,
    { name: "AES-GCM", length: 256 },
    false,
    usage
  );
}

export async function encryptAesGcm(key, plaintextBytes, nonce) {
  const subtle = getSubtleCrypto();
  const ciphertext = await subtle.encrypt(
    { name: "AES-GCM", iv: nonce },
    key,
    plaintextBytes
  );
  return new Uint8Array(ciphertext);
}

export async function decryptAesGcm(key, ciphertextBytes, nonce) {
  const subtle = getSubtleCrypto();
  const plaintext = await subtle.decrypt(
    { name: "AES-GCM", iv: nonce },
    key,
    ciphertextBytes
  );
  return new Uint8Array(plaintext);
}

export function utf8Encode(text) {
  return encoder.encode(text);
}

export function utf8Decode(bytes) {
  return decoder.decode(bytes);
}

export async function exportKeyRaw(key) {
  const subtle = getSubtleCrypto();
  return await subtle.exportKey('raw', key);
}
