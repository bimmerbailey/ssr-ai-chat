db = db.getSiblingDB('rag_app');
db.createUser(
    {
        user: 'rag_user',
        pwd: 'password',
        roles: [
            {role: 'readWrite', db: 'rag_app'},
        ],
    },
);
db.createCollection('users');

db = db.getSiblingDB('test_rag_app');
db.createUser(
    {
        user: 'rag_user',
        pwd: 'password',
        roles: [
            {role: 'readWrite', db: 'test_rag_app'}
        ],
    },
);
db.createCollection('users');
