=== mix



=== Machine à état des pages

```mermaid
  graph TD;
  subgraph "client html"
     index["index.html"] 
     photo["photo.html"]
     manual["manual.html"]
     
     cookie[("cookie \nGroupe+Equipe")]     

     photo -- noPhotoBtn --> manual

     cookphoto{ }

  end
  subgraph "serveur flask"

     save{save.json}
     mix{mix.json}
     
     results{results.json}
     root["/"]
     setgroup([/set_group])
     ajaxphoto["/photo"]
     rendermanual["/manual"]

     root -- "render" --> index
     index -- logInButton --> setgroup
     setgroup -- init --> cookie & save & mix & results 
     cookie -- successsetgroup --> rendermanual

     ajaxphoto -- cookie présent --> cookphoto --> photo
     ajaxphoto -- cookie absent --> root
     cookie --> cookphoto
     rendermanual -- render --> manual
  end
```


=== dev

Dans le local "serveur2"

 - git pull
 Si pb et tu veux pas garder tes modifs 
      - git reset --hard

 - tu travailles
 - git add .
 - git commit -m"message ;;; "
 - git push

 Là github est à jour mais pas le serveur

    - ssh user@srv-geitp -p2222 "cd /var/www/html; git pull"

    