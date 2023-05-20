# Juego multijugador
Hemos creado dos juegos, uno multijugador que se puede ejecutar en varios ordenadores (player3.py y sala3.py) y otro también multijugador pero que se juega con el teclado de un solo ordenador (basic.py).<br />
El primero trata sobre dos jugadores, uno a la izquierda del escenario y otro a la derecha que sólo pueden moverse hacia arriba y hacia abajo. Ambos pueden disparar balas que van en dirección recta hacia el otro lado y si le da al contrincante, obtiene un punto. La idea era que al dar a la tecla SPACE, se crease una bala y apareciese en pantalla viajando hacia el lado contrario y luego desapareciese, como ocurre en basic.py. Sin embargo, en nuestro programa se dibuja la misma bala múltiples veces a lo largo de su trayecto y no desaparece, no conseguimos solucionarlo. <br />
El segundo, basic.py, se trata de un space shooter multijugador. Hay dos jugadores, cada uno con su puntuaje, que tienen que disparar a unos meteoritos que aparecen de manera aleatoria. Si alguno de los jugadores colisiona con algún meteorito, el juego acaba para los dos jugadores.<br />
Las imágenes para ambos juegos se encuentran en la carpeta img.<br /> <br />
**sala3.py** <br />
Tenemos la clase Player() que tiene la posición en donde empieza y luego los métodos moveDown() y moveUp() para que se mueva hacia abajo y hacia arriba. También tiene el método shoot() que crea una bola en la posición en la que se encuentre el jugador. <br />
La clase Ball() requiere de una posición pos, del lado side de donde sale la bola y un identificador id. El side es necesario pues si sale del jugador izquierdo, se tiene que mover hacia la derecha y viceversa. El id sirve para, posteriormente, identificar las bolas que se salen del escenario, eliminarlas y mandarle esa información a player3.py para que las deje de dibujar (esto es lo que nos falla).<br />
En la clase Game() inicializamos los jugadores, y las bolas del jugador izquierdo y las bolas del jugador derecho como listas vacías (self.ballsleft y self.ballsrigth) ya que al principio nadie ha disparado nada.
La lista seld.id_malos contendrá los identificadores de las bolas que deberían desaparecer. Para ello, tenemos el método move.ball() que compara la posición de la bola con el tamaño del escenario, si se sale o es negativo ( en caso de una bola del jugador derecho) añadimos su identificador a la lista id_malos y la removemos de la lista que la contiene (self.ballsleft o self.ballsright). <br />
Seguimos en la clase Game(). El método shoot_player() se ejecuta cuando recibe el comando 'shoot' que se produce al usar la tecla SPACE. Aquí se aumenta el self.contador_balls.value que será el identificador dado a la nueva bola creada. El método collide_player() se produce cuando recibe la información 'collide' de alguno de los jugadores. Si viene del jugador izquierdo, se debe a que el jugador derecho ha conseguido darle con alguna de sus balas y, por tanto, consigue un punto. Ocurre de manera análoga si el comando viene del jugador derecho. <br />
Por último, en get_info() mandamos la información a player3.py para que dibuje todo. En pos_left_ball y pos_right_ball lo que mandamos son listas suyos elementos son duplas, el primer elemento es la posición de la bola y el segundo elemento su identificador. Son listas de las bolas que dispara cada jugador. También enviamos la lista de id_malos. <br /> <br />
**player3.py**<br />
En la clase Game() obtenemos la información de sala3.py y establecemos todas las posiciones e identificadores.<br />
La clase Paddle() dibuja al jugador y la clase BallSprite() se encarga de la bola. <br />
En l aclase Display() inicializamos la pantalla y creamos los grupos de sprites: self.all_sprites, self.paddle_group, self.balls1_group (bolas que lanza el jugador izquierdo) y self.balls2_group (bolas que lanza el jugador derecho). <br />
En el método analyze_events() de la clase Display(), vemos si alguna de las balas del jugador derecho colisiona con el jugador izquierdo con  hit = pygame.sprite.spritecollide(self.paddles[LEFT_PLAYER], self.balls2_group, False) y viceversa. En caso afirmativo, le enviamos esa información de 'collide' a sala para que cambie el puntuaje de cada jugador. <br />
En el refresh() de Display() vamos creando los sprites de las bolas y añadiéndolas a self.all_sprites para posteriormente dibujar todo. Además, recorremos la lista de id_malos que viene de sala y lo comparamos con los identificadores de las bolas que tenemos, para, si alguno coincide, eliminarlo de la pantalla.<br />





