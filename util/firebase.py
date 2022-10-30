import firebase_admin

def InitFirebaseApp(baseDir):
    cred=firebase_admin.credentials.Certificate(str(baseDir.joinpath('firebase.json')))
    app=firebase_admin.initialize_app(cred)
    return app