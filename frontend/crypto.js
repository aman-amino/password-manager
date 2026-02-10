const encoder = new TextEncoder();
const decoder = new TextDecoder();

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
  crypto.getRandomValues(bytes);
  return bytes;
}

export async function importPassword(password) {
  return crypto.subtle.importKey(
    "raw",
    encoder.encode(password),
    { name: "PBKDF2" },
    false,
    ["deriveKey", "deriveBits"]
  );
}

export async function deriveRootKey(passwordKey, salt, iterations) {
  return crypto.subtle.deriveKey(
    {
      name: "PBKDF2",
      salt,
      iterations,
      hash: "SHA-256",
    },
    passwordKey,
    { name: "HKDF", hash: "SHA-256", length: 256 },
    false,
    ["deriveKey", "deriveBits"]
  );
}

export async function deriveSubKey(rootKey, info, usage) {
  return crypto.subtle.deriveKey(
    {
      name: "HKDF",
      hash: "SHA-256",
      salt: new Uint8Array([]),
      info: encoder.encode(info),
    },
    rootKey,
    { name: "AES-GCM", length: 256 },
    false,
    usage
  );
}

export async function encryptAesGcm(key, plaintextBytes, nonce) {
  const ciphertext = await crypto.subtle.encrypt(
    { name: "AES-GCM", iv: nonce },
    key,
    plaintextBytes
  );
  return new Uint8Array(ciphertext);
}

export async function decryptAesGcm(key, ciphertextBytes, nonce) {
  const plaintext = await crypto.subtle.decrypt(
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
