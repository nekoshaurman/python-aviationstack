### Команды

Рейсы  
aero-claude flight <номер>                     Статус рейса                        ✅ free                                                                                                                                 
aero-claude flight <номер> --watch             Следить за рейсом каждые 60 сек     ✅ free                                                                                                                                 

AIRPORT можно сделать как AIRLINE чтобы кешить и потом оттуда брать инфу  
Аэропорты                                                                                                                                
aero-claude airport <IATA>                            Карточка аэропорта       ❌ basic and better
aero-claude airport <IATA> --arrivals                 Прилёты в аэропорт       ✅ free                                                                                                                                     
aero-claude airport <IATA> --departures               Вылеты из аэропорта      ✅ free                                                                                                                                     
aero-claude airport <IATA> --arrivals --limit <N>     Прилёты, N рейсов        ✅ free                                                                                                                                     
aero-claude airport <IATA> --departures  --limit <N>  Вылеты, N рейсов         ✅ free    

Авиакомпании  
aero-claude airline <IATA>                           Карточка авиакомпании            ✅ free (but using cache from /airlines npt / airline)                                                                                                                              
aero-claude airline <IATA> --flights                 Активные рейсы авиакомпании      ✅ free                                                                                                                              
aero-claude airline <IATA> --flights --limit <N>     Активные рейсы, N штук           ✅ free

Watchlist                                                                                                                            
aero-claude watch add <номер>                  Добавить рейс в watchlist          💾 local                                                                                                                                
aero-claude watch remove <номер>               Удалить рейс из watchlist          💾 local                                                                                                                                
aero-claude watch list                         Показать все рейсы в watchlist     💾 local                                                                                                                                
aero-claude watch clear                        Очистить весь watchlist            💾 local

История и статистика  
aero-claude history                            История всех запросов            💾 local                                                                                                                                  
aero-claude history --limit <N>                История, последние N записей     💾 local                                                                                                                                  
aero-claude history --clear                    Очистить историю                 💾 local                                                                                                                                  
aero-claude stats                              Статистика использования         💾 local