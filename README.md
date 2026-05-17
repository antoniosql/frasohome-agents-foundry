# FraSoHome Agents Foundry

Demo técnica para construir un sistema de agentes en Microsoft Foundry a partir de un caso retail omnicanal ficticio: **FraSoHome**, una cadena de hogar y decoración con tiendas físicas, e-commerce, CRM, inventario, pagos, devoluciones y problemas realistas de calidad de datos.

El repositorio permite enseñar el mismo caso por dos caminos:

- **Portal de Microsoft Foundry:** diseñador de agentes, File Search, Code Interpreter, workflows visuales, Playground y trazas.
- **Código Python:** creación de agentes con SDK, carga de conocimiento, análisis de CSVs, ejecución de prompts y orquestación multiagente.

## Caso de negocio

FraSoHome tiene datos suficientes para tomar mejores decisiones, pero están repartidos entre sistemas y no forman una verdad operativa común:

- CRM y fidelización.
- POS de tienda física.
- Pedidos y pagos e-commerce.
- Devoluciones online y en tienda.
- Catálogo, SKUs, productos y stock.
- Políticas internas de operación, devolución, KPIs, pagos y atención.

El objetivo de la demo es construir un sistema agentic que responda preguntas de negocio con evidencia:

- ¿Qué política aplica a una devolución omnicanal?
- ¿Qué problemas de calidad tienen los datos?
- ¿Por qué podrían subir las devoluciones online en una categoría?
- ¿Qué acción de 7 días recomendaríamos y con qué métrica de seguimiento?

## Arquitectura de agentes

La demo propone un sistema multiagente con especialistas:

| Agente | Función | Herramienta principal |
|---|---|---|
| `frasohome-knowledge` | Responde sobre políticas, FAQ y contexto del caso | File Search |
| `frasohome-data-quality` | Perfila CSVs, detecta nulos, duplicados y anomalías | Code Interpreter |
| `frasohome-returns` | Analiza devoluciones, motivos, canales y reglas aplicables | File Search / contexto |
| `frasohome-operations` | Revisa stock, tienda, pagos, conciliación, pedidos y SKUs | File Search / contexto |
| `frasohome-storyteller` | Sintetiza evidencias en una recomendación ejecutiva | Sin herramienta |
| `frasohome-orchestrator` | Coordina especialistas y aplica validación humana si baja la confianza | Workflow o Python |

Contrato de salida recomendado:

```json
{
  "pregunta": "",
  "causa_probable": "",
  "evidencias": [
    {
      "fuente": "",
      "calculo": "",
      "valor": ""
    }
  ],
  "riesgos": [],
  "accion_7_dias": "",
  "metrica_seguimiento": "",
  "requiere_validacion_humana": true
}
```

## Estructura del repositorio

```text
.
├── agents.md
├── README.md
├── README_CODE.md
├── requirements.txt
├── pyproject.toml
├── .env.example
├── notebooks/
│   └── frasohome_foundry_agents_demo.ipynb
├── case/
│   ├── fraso_home_caso.md
│   ├── fraso_home_storytelling_foundry.md
│   ├── plan_sesion_practica_foundry_frasohome.md
│   ├── paso_a_paso_portal_foundry_agents_workflows.md
│   ├── data/
│   │   └── *.csv
│   └── kb/
│       ├── README.md
│       ├── *.docx
│       ├── FS-KB-*.md
└── src/
    └── frasohome_agents/
        ├── cli.py
        ├── create_agents.py
        ├── foundry.py
        ├── local_data_quality.py
        ├── orchestrator.py
        └── prompts.py
```

## Base de conocimiento

La carpeta `case/kb` contiene políticas internas para File Search:

- Política de devoluciones omnicanal.
- Diccionario de KPIs y reglas de cálculo.
- Manual de tienda, caja y pagos mixtos.
- Guía de conciliación de pagos e-commerce.
- Taxonomía de catálogo y reglas SKU.
- Guía de fidelización CRM.
- FAQ interna de operaciones y atención.

Para el agente `frasohome-knowledge`, cargar en File Search:

- `case/fraso_home_caso.md`
- todos los archivos de `case/kb/FS-KB-*.md`

## Datos

Los CSV sintéticos están en `case/data` e incluyen:

- `crm.csv`
- `pedidos.csv`
- `lineas_pedido.csv`
- `devoluciones_online.csv`
- `devoluciones_tienda.csv`
- `ventas_pos.csv`
- `pagos_tienda.csv`
- `productos.csv`
- `stock_diario.csv`
- `tiendas.csv`
- `fact_transacciones.csv`

El caso incluye problemas intencionados de calidad: nulos, duplicados, claves inconsistentes, formatos heterogéneos, fechas problemáticas, importes/cantidades anómalas y stock irregular.

## Quickstart por portal

Sigue el paso a paso:

[case/paso_a_paso_portal_foundry_agents_workflows.md](case/paso_a_paso_portal_foundry_agents_workflows.md)

Resumen:

1. Crear `frasohome-knowledge` con File Search y cargar caso + KB.
2. Crear `frasohome-data-quality` con Code Interpreter y cargar CSVs.
3. Crear especialistas `returns`, `operations` y `storyteller`.
4. Crear workflow `frasohome-orchestrator`.
5. Probar los prompts canónicos en Playground.
6. Mostrar historial, tool calls, trazas u observabilidad.

## Quickstart por código

Consulta la guía detallada:

[README_CODE.md](README_CODE.md)

También puedes ejecutar la demo paso a paso desde el notebook:

[notebooks/frasohome_foundry_agents_demo.ipynb](notebooks/frasohome_foundry_agents_demo.ipynb)

Preparación rápida:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
copy .env.example .env
az login
```

Edita `.env`:

```powershell
PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project>
MODEL_DEPLOYMENT=<deployment-name>
```

Validar assets y perfilar datos localmente:

```powershell
frasohome-agents check-assets
frasohome-agents local-profile
```

Previsualizar y crear agentes:

```powershell
frasohome-agents create-agents --dry-run
frasohome-agents create-agents
```

Ejecutar demos:

```powershell
frasohome-agents demo-knowledge
frasohome-agents demo-data-quality
frasohome-agents demo-orchestrator
```

## Prompts canónicos

Knowledge:

```text
Un cliente compró un sofá online, quiere devolverlo en tienda y usó un cupón. ¿Qué pasos debe seguir atención al cliente?
```

Data Quality:

```text
Analiza los CSV de FraSoHome. Genera un Data Quality Report con tabla resumen y cinco acciones de limpieza priorizadas antes de crear features o dashboards.
```

Multiagente:

```text
¿Por qué están subiendo las devoluciones online en iluminación y qué haríamos esta semana?
```

## Documentación del repo

- [agents.md](agents.md): playbook de desarrollo de agentes en Foundry.
- [README_CODE.md](README_CODE.md): ejecución por código con Python.
- [case/plan_sesion_practica_foundry_frasohome.md](case/plan_sesion_practica_foundry_frasohome.md): plan de sesión práctica.
- [case/paso_a_paso_portal_foundry_agents_workflows.md](case/paso_a_paso_portal_foundry_agents_workflows.md): guía portal paso a paso.
- [case/fraso_home_caso.md](case/fraso_home_caso.md): caso base convertido a Markdown.
- [case/fraso_home_storytelling_foundry.md](case/fraso_home_storytelling_foundry.md): storytelling extraído de la presentación.
- [case/kb/README.md](case/kb/README.md): índice de políticas y guías.

## Buenas prácticas incluidas

- Separación entre conocimiento, cálculo y síntesis.
- File Search para grounding documental.
- Code Interpreter para cálculos sobre CSVs.
- Contratos JSON entre agentes.
- Validación humana cuando hay baja confianza o conflicto documental.
- Uso de Entra ID/RBAC en lugar de secretos embebidos.
- Trazabilidad de tool calls y conversaciones.
- Preparación para observabilidad y evaluación.

## Requisitos

- Python 3.10 o superior.
- Proyecto de Microsoft Foundry con modelo desplegado.
- Permisos para crear agentes, cargar archivos y ejecutar herramientas.
- Azure CLI autenticado con `az login`.

## Nota

FraSoHome es un caso ficticio con datos sintéticos. Está diseñado para demos, formación y hackathons sobre agentes, preparación de datos, grounding, workflows y evaluación en Microsoft Foundry.
