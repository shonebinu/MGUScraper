{ pkgs ? import <nixpkgs> {} }:
let
  my-python-packages = ps: with ps; [
    streamlit
    scrapy
  ];
  my-python = pkgs.python3.withPackages my-python-packages;
in my-python.env
