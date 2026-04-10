# Notes v3

## Чем v3 отличается от v2
- больше примеров с явными заголовками 4 шагов
- больше replacement-oriented ответов
- больше safest-default reasoning
- меньше мягких формулировок
- сильнее закреплён вывод "anti-pattern -> replacement -> why -> next steps"

## Когда считать v3 успешным
Если на главном кейсе модель отвечает близко к такой форме:

1. Важный контекст: ...
2. Рекомендуемый паттерн: File exchange как основной online-механизм — anti-pattern; нужен gateway + integration layer.
3. Почему: ...
4. Следующие шаги: ...

## После v3
Если v3 даст хороший ответ, следующий шаг — head-to-head comparison:
- 7B base + landscape
- 7B base + landscape + skills
- 7B LoRA v3 + landscape
