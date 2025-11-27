import os
import re
import hashlib
from dotenv import load_dotenv
from supabase import create_client, Client
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

# --- 1. CONFIGURACIÓN INICIAL ---
print("🚀 Iniciando el script de ingestión de documentos (Versión Mejorada)...")
load_dotenv('.env.local')

SUPABASE_URL = os.environ.get("VITE_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("VITE_SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("❌ Las variables de entorno de Supabase no están configuradas.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("🧠 Cargando modelo de embeddings 'all-MiniLM-L6-v2'...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("✅ Modelo cargado.")

# --- 2. FUNCIONES DE PROCESAMIENTO DE TEXTO ---

def clean_pdf_text(text: str) -> str:
    """
    Limpia el texto extraído de un PDF.
    - Une palabras cortadas por guiones al final de una línea.
    - Normaliza los espacios en blanco y saltos de línea.
    """
    text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def split_text_into_semantic_chunks(text: str, max_chars: int = 1000, overlap: int = 150) -> list[str]:
    """
    Divide el texto en chunks semánticamente coherentes (basado en frases).
    """
    sentences = re.split(r'(?<=[.?!])\s+', text)
    if not sentences:
        return []

    chunks = []
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 < max_chars:
            current_chunk += sentence + " "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            
            # El overlap asegura que el inicio del nuevo chunk contenga el final del anterior
            start_index = max(0, len(current_chunk) - overlap)
            current_chunk = current_chunk[start_index:].strip() + " " + sentence + " "
            
    if current_chunk:
        chunks.append(current_chunk.strip())
        
    return chunks

def get_file_hash(file_path: str) -> str:
    """Calcula el hash SHA256 de un archivo para evitar duplicados."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

# --- 3. LÓGICA PRINCIPAL ---

def main():
    path_to_documents = 'documentos_a_procesar'
    if not os.path.exists(path_to_documents):
        os.makedirs(path_to_documents)
        print(f"📂 Se creó la carpeta '{path_to_documents}'. Agrega tus PDFs y vuelve a ejecutar.")
        return

    for filename in os.listdir(path_to_documents):
        if not filename.lower().endswith('.pdf'):
            continue

        file_path = os.path.join(path_to_documents, filename)
        print(f"\n--- Procesando: {filename} ---")

        # 1. Evitar duplicados
        file_hash = get_file_hash(file_path)
        result = supabase.table('documents').select('id').eq('file_hash', file_hash).execute()
        if result.data:
            print(f"🟡 Documento ya procesado. Saltando.")
            continue

        # 2. Extraer y limpiar texto
        try:
            reader = PdfReader(file_path)
            raw_text = "".join(page.extract_text() for page in reader.pages if page.extract_text())
            clean_text = clean_pdf_text(raw_text)
            total_pages = len(reader.pages)
        except Exception as e:
            print(f"❌ Error al leer el PDF '{filename}': {e}")
            continue
        
        if not clean_text:
            print(f"⚠️ No se pudo extraer texto de '{filename}'. Saltando.")
            continue

        # 3. Registrar el documento
        doc_data = { 'filename': filename, 'file_hash': file_hash, 'total_pages': total_pages }
        doc_res = supabase.table('documents').insert(doc_data).execute()
        document_id = doc_res.data[0]['id']
        print(f"📄 Documento '{filename}' registrado con ID: {document_id}")

        # 4. Dividir, generar embeddings y guardar chunks
        chunks = split_text_into_semantic_chunks(clean_text)
        
        for i, chunk_text in enumerate(chunks):
            embedding = model.encode(chunk_text).tolist()
            chunk_data = {
                'document_id': document_id,
                'chunk_text': chunk_text,
                'chunk_index': i,
                'embedding': embedding
            }
            supabase.table('document_chunks').insert(chunk_data).execute()
        
        print(f"💾 {len(chunks)} chunks de texto limpio guardados.")

        # 5. Marcar como procesado
        supabase.table('documents').update({'processed': True}).eq('id', document_id).execute()

    print("\n\n✅ ¡Proceso de ingestión finalizado con éxito!")

if __name__ == "__main__":
    main()