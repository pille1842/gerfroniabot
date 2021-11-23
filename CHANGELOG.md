# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.1] - 2021-11-23
### Added
- A changelog is now kept in this file.
- The bot can now keep people in quarantine.
- A parameter QUARANTINE_CHANNEL_ID has been added for this purpose. You need to set it for the bot to work.

### Changed
- The message "A voice chat is taking place in ..." is now put in bold.
- When referring to voice channels, they are no longer preceded by "#" to distinguish them from text channels.
- The bot will not keep a guestbook for the quarantine channel (QUARANTINE_CHANNEL_ID).
