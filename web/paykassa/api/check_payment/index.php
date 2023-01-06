<?php // SCI | Check payment (sci_confirm_order)

$config = require_once('../../inc/config.php');

if (($_SERVER["REQUEST_METHOD"]=="POST") && (!empty($config))) {

	require_once('../../inc/classes/paykassa_sci.class.php');

	// Получение и установка переменных

	$data = json_decode(file_get_contents('php://input'), true);

	$data['sci_id'] = $config['sci']['sci_id'];

	$data['sci_key'] = $config['sci']['sci_key'];

	if (!isset($data['test'])) { $data['test'] = false; }

	if (!empty($data["private_hash"])) {

		$paykassa = new PayKassaSCI($data['sci_id'], $data['sci_key'], $test);

		$res = $paykassa->sci_confirm_order($data["private_hash"]);

		if ($res['error']) {

			header('Content-Type: application/json; charset=UTF-8');
			echo json_encode(['err' => $res['message']], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_NUMERIC_CHECK);

		} else {

			header('Content-Type: application/json; charset=UTF-8');
			echo json_encode($res['data'], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_NUMERIC_CHECK);

		}

	}

}