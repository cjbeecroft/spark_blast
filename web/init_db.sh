query1=$(curl -X POST -H "Content-Type: application/json" -u dbalck:welcome1111 -d '{ "name": "query1", "sequence": "ATAGTTT"}' 'localhost:8000/queries/' | jq '{name: "job1", query: .id , status: "IP" }')
query2=$(curl -X POST -H "Content-Type: application/json" -u dbalck:welcome1111 -d '{ "name": "query2", "sequence": "TGCATAGCTT" }' 'localhost:8000/queries/' | jq '{name: "job2", query: .id, status: "IP" }')


curl -X POST -H "Content-Type: application/json" -u dbalck:welcome1111 -d "$query1" 'localhost:8000/jobs/'
curl -X POST -H "Content-Type: application/json" -u dbalck:welcome1111 -d "$query2" 'localhost:8000/jobs/'


curl -X POST -H "Content-Type: application/json" -u dbalck:welcome1111 -d "{}" 'localhost:8000/jobs/'
curl -X POST -H "Content-Type: application/json" -u dbalck:welcome1111 -d "$query2" 'localhost:8000/jobs/'

    creator = models.ForeignKey('auth.User', related_name='data', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default='Default_Datum_Name')
    created = models.DateTimeField(auto_now_add=True)
    location = models.URLField(default='swift.example.com/object1')