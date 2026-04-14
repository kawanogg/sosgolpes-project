<?php
function conectarBanco(): PDO {
    $host = getenv('DB_HOST');
    $db   = getenv('MYSQL_DATABASE');
    $user = 'root';
    $pass = getenv('MYSQL_ROOT_PASSWORD');
    $charset = 'utf8mb4';

    $dsn = "mysql:host=$host;dbname=$db;charset=$charset";
    $options = [
        PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        PDO::ATTR_EMULATE_PREPARES   => false,
    ];

    return new PDO($dsn, $user, $pass, $options);
}
?>
