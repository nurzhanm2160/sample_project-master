<?php // Functions

// Проверка обязательных переменных
function check_var($data, $required_var) {

	foreach ($required_var as $key) {

		if (!array_key_exists($key, $data)) {

			return $key.' required';
		
		}

	}

}