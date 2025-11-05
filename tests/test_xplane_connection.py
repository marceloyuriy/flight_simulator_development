"""
Teste rápido da conexão com X-Plane
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_xplane_connection():
    """Testa se podemos importar e conectar com X-Plane"""
    print("🧪 TESTANDO CONEXÃO COM X-PLANE")
    print("=" * 50)

    try:
        import XPlaneConnect as xpc
        print("✅ XPlaneConnect importado com sucesso!")

        # Tenta conectar com X-Plane
        try:
            client = xpc.XPlaneConnect()
            print("✅ Cliente X-Plane criado!")

            # Tenta obter dados de posição
            posi = client.getPOSI()
            print(f"✅ Dados de posição obtidos: {posi}")

            client.close()
            print("✅ Conexão fechada corretamente")

            return True

        except Exception as e:
            print(f"⚠️  X-Plane não está rodando ou há problema de conexão: {e}")
            print("   - Certifique-se que o X-Plane está executando")
            print("   - E que está configurado para aceitar conexões UDP na porta 49000")
            return False

    except ImportError as e:
        print(f"❌ Não foi possível importar XPlaneConnect: {e}")
        return False


if __name__ == "__main__":
    success = test_xplane_connection()

    if success:
        print("\n🎉 X-Plane Connect está funcionando!")
    else:
        print("\n💥 Há problemas com a conexão do X-Plane")
        print("   Vamos continuar com um mock para desenvolvimento")