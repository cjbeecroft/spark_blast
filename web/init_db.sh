query1=$(curl -X POST -H "Content-Type: application/json" -u dbalck:llendxer -d '{ "name": "query1", "sequence": "ATAGTTT"}' 'localhost:8000/queries' | jq '{name: "job1", query: .id , status: "IP" }')
query2=$(curl -X POST -H "Content-Type: application/json" -u dbalck:llendxer  -d '{ "name": "query2", "sequence": "TGCATAGCTT" }' 'localhost:8000/queries' | jq '{name: "job2", query: .id, status: "IP" }')


curl -X POST -H "Content-Type: application/json" -u dbalck:llendxer  -d "$query1" 'localhost:8000/jobs'
curl -X POST -H "Content-Type: application/json" -u dbalck:llendxer  -d "$query2" 'localhost:8000/jobs'
