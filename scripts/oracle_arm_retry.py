"""
Script para tentar criar instância ARM Oracle Cloud automaticamente
Fica tentando até conseguir capacidade disponível

IMPORTANTE: Configure as variáveis no início do script antes de rodar!
"""

import oci
import time
import logging
from datetime import datetime

# ===== CONFIGURAÇÃO - EDITE AQUI =====
# Você encontra esses valores no Oracle Cloud Console

# Compartment OCID (Dashboard → Identity → Compartments → Copiar OCID)
COMPARTMENT_ID = "ocid1.compartment.oc1..seu-compartment-id-aqui"

# Availability Domain (Ex: "AD-1", "AD-2", "AD-3")
# Tente diferentes ADs se um não funcionar
AVAILABILITY_DOMAIN = "AD-1"

# Subnet OCID (Networking → Virtual Cloud Networks → Sua VCN → Subnets → Copiar OCID)
SUBNET_ID = "ocid1.subnet.oc1..sua-subnet-id-aqui"

# Image OCID para Ubuntu 22.04 ARM
# Você encontra em: Compute → Images → Ubuntu (Buscar por ARM)
IMAGE_ID = "ocid1.image.oc1..ubuntu-22-04-aarch64-aqui"

# SSH Public Key (conteúdo do seu arquivo ~/.ssh/id_rsa.pub)
SSH_PUBLIC_KEY = """ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC... seu-ssh-public-key-aqui"""

# Nome da instância
INSTANCE_NAME = "afiliadobot-backend"

# Shape ARM Free Tier
SHAPE_NAME = "VM.Standard.A1.Flex"
OCPUS = 4  # Max free tier ARM
MEMORY_GB = 24  # Max free tier ARM

# Tempo entre tentativas (segundos)
RETRY_INTERVAL = 60  # Tenta a cada 1 minuto

# ===== FIM DA CONFIGURAÇÃO =====

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('oracle_retry.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def create_instance():
    """Tenta criar a instância ARM"""
    
    # Configuração OCI (usa credenciais padrão de ~/.oci/config)
    config = oci.config.from_file()
    compute_client = oci.core.ComputeClient(config)
    
    # Detalhes da instância
    instance_details = oci.core.models.LaunchInstanceDetails(
        availability_domain=AVAILABILITY_DOMAIN,
        compartment_id=COMPARTMENT_ID,
        display_name=INSTANCE_NAME,
        shape=SHAPE_NAME,
        shape_config=oci.core.models.LaunchInstanceShapeConfigDetails(
            ocpus=OCPUS,
            memory_in_gbs=MEMORY_GB
        ),
        source_details=oci.core.models.InstanceSourceViaImageDetails(
            image_id=IMAGE_ID,
            source_type="image"
        ),
        create_vnic_details=oci.core.models.CreateVnicDetails(
            subnet_id=SUBNET_ID,
            assign_public_ip=True
        ),
        metadata={
            "ssh_authorized_keys": SSH_PUBLIC_KEY
        }
    )
    
    try:
        logger.info("🚀 Tentando criar instância ARM...")
        response = compute_client.launch_instance(instance_details)
        
        logger.info("✅ SUCESSO! Instância criada!")
        logger.info(f"Instance ID: {response.data.id}")
        logger.info(f"Status: {response.data.lifecycle_state}")
        
        return True, response.data
        
    except oci.exceptions.ServiceError as e:
        if "Out of capacity" in str(e) or "OutOfCapacity" in str(e):
            logger.warning("⏳ Sem capacidade disponível ainda...")
            return False, None
        else:
            logger.error(f"❌ Erro inesperado: {e}")
            return False, None


def main():
    """Loop principal de retry"""
    
    logger.info("="*60)
    logger.info("🤖 Oracle Cloud ARM Auto-Retry")
    logger.info("="*60)
    logger.info(f"Shape: {SHAPE_NAME}")
    logger.info(f"OCPUs: {OCPUS}, RAM: {MEMORY_GB}GB")
    logger.info(f"Availability Domain: {AVAILABILITY_DOMAIN}")
    logger.info(f"Intervalo entre tentativas: {RETRY_INTERVAL}s")
    logger.info("="*60)
    logger.info("Pressione Ctrl+C para parar")
    logger.info("")
    
    attempt = 0
    
    try:
        while True:
            attempt += 1
            logger.info(f"📍 Tentativa #{attempt} - {datetime.now().strftime('%H:%M:%S')}")
            
            success, instance = create_instance()
            
            if success:
                logger.info("")
                logger.info("="*60)
                logger.info("🎉 MÁQUINA CRIADA COM SUCESSO!")
                logger.info("="*60)
                logger.info(f"🆔 Instance ID: {instance.id}")
                logger.info("")
                logger.info("📋 Próximos passos:")
                logger.info("1. Aguarde a instância ficar 'RUNNING'")
                logger.info("2. Conecte via SSH: ssh ubuntu@<IP_PUBLICO>")
                logger.info("3. Faça deploy do backend")
                logger.info("")
                logger.info("Verifique no Oracle Console:")
                logger.info("https://cloud.oracle.com/compute/instances")
                logger.info("="*60)
                break
            
            logger.info(f"💤 Aguardando {RETRY_INTERVAL}s antes da próxima tentativa...")
            time.sleep(RETRY_INTERVAL)
            
    except KeyboardInterrupt:
        logger.info("")
        logger.info("⚠️  Script interrompido pelo usuário")
        logger.info(f"Total de tentativas: {attempt}")
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")


if __name__ == "__main__":
    # Validação básica
    if "seu-" in COMPARTMENT_ID or "seu-" in SUBNET_ID:
        print("❌ ERRO: Configure as variáveis no início do script primeiro!")
        print("Edite o script e preencha:")
        print("  - COMPARTMENT_ID")
        print("  - SUBNET_ID")
        print("  - IMAGE_ID")
        print("  - SSH_PUBLIC_KEY")
        exit(1)
    
    main()
