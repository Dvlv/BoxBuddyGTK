#!/bin/bash
flatpak-builder --repo=repo --force-clean build-dir co.uk.dvlv.boxbuddy.yml
flatpak build-bundle repo boxbuddy.flatpak co.uk.dvlv.boxbuddy
