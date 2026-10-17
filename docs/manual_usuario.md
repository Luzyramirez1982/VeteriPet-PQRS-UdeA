# 10. Manual de Usuario - VeteriPet UdeA

## 1. ¿Qué es?
VeteriPet UdeA es un programa de consola en Python para registrar, consultar y hacer seguimiento a las PQRS (Peticiones, Quejas, Reclamos y Sugerencias) de atención veterinaria de perros y gatos en la Universidad de Antioquia.

## 2. Requisitos
- Python 3.10 o superior.
- Carpeta `data/` con los archivos `Peticion.txt`, `Queja.txt`, `Reclamo.txt` y `Sugerencia.txt` (el programa los usa para guardar la información).

## 3. Cómo ejecutarlo
1. Descargue o clone el repositorio.
2. Abra una terminal en la carpeta del proyecto.
3. Ejecute el script principal que está en `src/`:
   ```bash
   python src/NOMBRE_DEL_SCRIPT_PRINCIPAL.py
   ```
   *(Reemplace por el nombre real del archivo principal.)*

## 4. Menú principal
```
Bienvenido a VeteriPet UdeA - Gestión de PQRS
  1. Registrar PQRS
  2. Consultar PQRS
  3. Registrar Cambio en PQRS
  4. Estadísticas
  5. Salir
```
Escriba el número de la opción y presione **Enter**.

## 5. Opción 1: Registrar PQRS
El programa solicita los datos uno por uno. Si un dato no es válido, muestra un mensaje y lo pide de nuevo.

| Campo | Regla |
| ----- | ----- |
| Nombre completo | 3 a 100 caracteres; solo letras, espacios, tildes, ñ, apóstrofes y guiones; sin números |
| Tipo de documento | CC, TI, CE, PP o NIT |
| Número de documento | 3 a 15 dígitos, solo números |
| Tipo de teléfono | Celular, Fijo, Corporativo u Otro |
| Teléfono de contacto | Exactamente 10 dígitos |
| Correo electrónico | Máximo 254 caracteres, con un único `@` y dominio válido |
| Dirección | Opcional; 5 a 200 caracteres. Si se omite se guarda como `N/A` |
| Tipo de solicitud | Petición, Queja, Reclamo o Sugerencia |
| Fecha de radicación | Fecha válida, no puede ser futura |
| Canal de recepción | Presencial, Correo electrónico, Página web, Teléfono, Redes sociales u Otro |
| Asunto o título | 5 a 150 caracteres |
| Descripción detallada | 20 a 2.000 caracteres, no solo espacios |
| Tipo de mascota | Perro o Gato |
| Campus relacionado | Uno de los 9 campus de la lista del programa |

Al terminar, el programa:
- asigna un **ID consecutivo** propio de cada tipo de solicitud,
- calcula la **fecha máxima de respuesta** (fecha de radicación + 30 días),
- deja el estado en **Registrada**,
- imprime el **radicado** en formato ASCII de 120 caracteres.

## 6. Opción 2: Consultar PQRS
Muestra el estado de las PQRS registradas. Cada una se visualiza como un radicado, con la misma presentación del comprobante.

## 7. Opción 3: Registrar cambio en PQRS
Permite cambiar el estado de una PQRS. El flujo es obligatorio y no se pueden saltar pasos:

`Registrada -> En proceso -> Solucionada`

## 8. Opción 4: Estadísticas
Muestra el promedio de días enteros que toma responder una PQRS (estadística obligatoria) y cinco estadísticas adicionales, por ejemplo:
1. Cantidad de registros por tipo de solicitud.
2. Cantidad de registros para perros y para gatos.
3. Documento o documentos más antiguos.
4. PQRS próximas a vencer.
5. Cantidad de PQRS por estado.

*(Ajuste esta lista a las estadísticas que implementó el equipo en `reportes.py`.)*

## 9. Opción 5: Salir
Cierra el programa. La información queda guardada en los archivos de `data/`.

## 10. Estructura del repositorio
```
/
├── src/      # Código fuente Python (.py)
├── docs/     # Documentación y manual de usuario
├── images/   # Logo y diagramas
└── data/     # Peticion.txt, Queja.txt, Reclamo.txt, Sugerencia.txt
```

## 11. Problemas frecuentes
| Problema | Solución |
| -------- | -------- |
| El programa rechaza un dato | Revise la regla del campo en la tabla de la sección 5 |
| No se puede pasar una PQRS a "Solucionada" | Primero debe estar "En proceso" |
| No encuentra los archivos | Verifique que existan en la carpeta `data/` |
