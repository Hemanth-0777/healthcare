<?php
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");
header("Access-Control-Allow-Methods: POST");
header("Access-Control-Allow-Headers: Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With");

require_once 'db_config.php';

$response = array();

try {
    // Get posted data
    $data = json_decode(file_get_contents("php://input"), true);
    
    if (isset($data['email']) && isset($data['password'])) {
        // Get user by email
        $stmt = $conn->prepare("SELECT id, name, email, password_hash, phone FROM users WHERE email = ?");
        $stmt->execute([$data['email']]);
        
        if ($stmt->rowCount() > 0) {
            $user = $stmt->fetch(PDO::FETCH_ASSOC);
            
            // Verify password
            if (password_verify($data['password'], $user['password_hash'])) {
                // Create response without password hash
                unset($user['password_hash']);
                $response["status"] = "success";
                $response["message"] = "Login successful";
                $response["user"] = $user;
                http_response_code(200);
            } else {
                throw new Exception("Invalid password");
            }
        } else {
            throw new Exception("User not found");
        }
    } else {
        throw new Exception("Missing required fields");
    }
} catch(Exception $e) {
    $response["status"] = "error";
    $response["message"] = $e->getMessage();
    http_response_code(401);
}

echo json_encode($response);
?>