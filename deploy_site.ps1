<#
	Script PowerShell para desplegar el contenido de `site/` a la rama `gh-pages`
	usando `git subtree push --prefix site origin gh-pages`.

	Uso:
		.\deploy_site.ps1

	Requisitos:
	- Tener el remote `origin` configurado hacia tu repositorio GitHub.
	- Autenticación configurada (SSH o credential helper) para poder push.
#>

if (-not (Test-Path .git)) {
	Write-Error "Este script debe ejecutarse desde la raíz del repositorio (donde está la carpeta .git)."
	exit 1
}

# Verificar que existe la carpeta site/
if (-not (Test-Path "site")) {
	Write-Error "No existe la carpeta 'site/'. Asegúrate de tener 'site/index.html'."
	exit 1
}

Write-Host "Preparando despliegue de 'site/' a la rama 'gh-pages'..."

# Asegurarse de que los cambios en main están commiteados
$st = git status --porcelain
if ($st) {
	Write-Host "Hay cambios sin commitear en la rama actual. Se recomienda commitearlos antes de hacer deploy."
	git status
	Read-Host "Presiona Enter para continuar o Ctrl+C para cancelar"
}

# Empujar usando subtree
try {
	git subtree push --prefix site origin gh-pages
	Write-Host "Despliegue completado. Si falla porque la rama gh-pages no existe, intenta crearla manualmente o usa el workflow de GitHub Actions en el repo remoto."
} catch {
	Write-Error "El despliegue con subtree falló: $_"
}

