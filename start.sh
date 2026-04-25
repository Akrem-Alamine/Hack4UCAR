#!/usr/bin/env bash
set -e

BLUE='\033[0;34m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

echo -e "${BLUE}╔══════════════════════════════════════════════╗"
echo -e "║   UCAR — Plateforme Intelligente            ║"
echo -e "╚══════════════════════════════════════════════╝${NC}"

# ── 1. Build & start all services ──────────────────────────
echo -e "\n${YELLOW}▶ Démarrage de tous les services Docker...${NC}"
docker compose up --build -d

# ── 2. Wait for backend to be healthy ──────────────────────
echo -e "${YELLOW}▶ Attente du backend...${NC}"
for i in $(seq 1 30); do
  if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✔ Backend opérationnel${NC}"
    break
  fi
  sleep 3
done

# ── 3. Run database migrations ─────────────────────────────
echo -e "${YELLOW}▶ Migrations de base de données...${NC}"
docker compose exec backend alembic upgrade head

# ── 4. Seed demo data ──────────────────────────────────────
echo -e "${YELLOW}▶ Chargement des données de démonstration...${NC}"
docker compose exec backend python scripts/seed_demo_data.py

echo -e "\n${GREEN}╔══════════════════════════════════════════════╗"
echo -e "║  ✔ Plateforme démarrée avec succès !         ║"
echo -e "╠══════════════════════════════════════════════╣"
echo -e "║  Local :  http://localhost                   ║"
echo -e "║  API   :  http://localhost/api/v1            ║"
echo -e "║  Docs  :  http://localhost/docs              ║"
echo -e "╚══════════════════════════════════════════════╝${NC}"

# ── 5. Cloudflare Tunnel (optional) ────────────────────────
if command -v cloudflared &> /dev/null; then
  echo -e "\n${YELLOW}▶ Démarrage du tunnel Cloudflare (accès internet)...${NC}"
  echo -e "${YELLOW}  Ctrl+C pour arrêter le tunnel (les services Docker continuent)${NC}\n"
  cloudflared tunnel --url http://localhost:80
else
  echo -e "\n${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${YELLOW}  Pour accès depuis internet, installe cloudflared :${NC}"
  echo -e ""
  echo -e "  ${BLUE}# Installation (une seule fois)${NC}"
  echo -e "  curl -L -o cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb"
  echo -e "  sudo dpkg -i cloudflared.deb"
  echo -e ""
  echo -e "  ${BLUE}# Lancer le tunnel (donne une URL publique instantanée)${NC}"
  echo -e "  cloudflared tunnel --url http://localhost:80"
  echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
fi
