REM sa password: SqlDevOps2017
docker login sqlpass.azurecr.io -u sqlpass -p QUXKtFF1BfbwplpWN3CXEuCeLId4+Odx
git clone https://github.com/erickangMSFT/wwi-db.git
cd wwi-db
docker-compose build 
docker-compose up -d

