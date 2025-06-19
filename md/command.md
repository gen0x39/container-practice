# kubectlコマンド
サービスが動いているのか確認
kubectl get svc -n bqnq
kubectl get deployment -n bqnq
kubectl get pods -n bqnq

# 最初にやること、クリーンアップ
1. サービスの削除
kubectl delete service <name> -n bqnq
kubectl delete service backend-service -n bqnq

2. Developmentの削除
kubectl delete deployment <name> -n bqnq



kubectl apply -f manifest/backend-development.yaml
kubectl apply -f manifest/backend-service.yaml
kubectl port-forward service/backend-service 8000:80 -n bqnq &
kubectl port-forward service/frontend-service 9700:80 -n bqnq & 




docker container ls
docker exec -it <container-id> ls
docker exec -it <container-id> bash


# apply
// kubectl port-forward pod/<container name> 8080:8080
kubectl get services -n bqnq
kubectl apply -f service.yaml
kubectl rollout restart deployment container-practice

kubectl logs <container name>
