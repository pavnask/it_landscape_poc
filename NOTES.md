# Notes

## Почему именно этот pack
Он заточен не на “общие знания”, а на:
- anti-pattern detection
- ambiguity handling
- reuse existing enterprise pattern
- controlled decommission
- 4-step architect answer shape

## Что будет честным сигналом успеха
После обучения 7B LoRA должна:
- увереннее говорить, что file exchange — плохой default для online-интеграции
- чаще выбирать integration layer / gateway
- меньше “колебаться”, чем 7B base
- лучше отвечать на ambiguous question

## Если train не стартует
Сначала проверь:
```bash
python -m mlx_lm.lora --help
```

Если конкретные флаги отличаются у твоей версии `mlx-lm`, пришли вывод help, и подстроим команды под неё.
