REM check if .env file exists

@echo off

SET "Ext=*.env"
SET FILE=%CD%\%Ext%

IF EXIST %FILE% (
    ECHO %FILE% exists
) ELSE (
    ECHO not found
	copy .env.example .env
)