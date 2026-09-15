#!/usr/bin/env bash
# FirstMate's existing profile flag owner, shared with workflow preflight.
fm_profile_shell_quote() {
  printf "'"
  printf '%s' "$1" | sed "s/'/'\\\\''/g"
  printf "'"
}

model_flag_for_harness() {
  local harness=$1 model=$2
  [ -n "$model" ] && [ "$model" != default ] || return 0
  case "$harness" in
    claude|codex|opencode|pi|pi-signed|grok|kimi|cursor|gemini|muse|rovo|omp|agy)
      printf -- '--model %s ' "$(fm_profile_shell_quote "$model")"
      ;;
  esac
}

effort_flag_for_harness() {
  local harness=$1 effort=$2 model=${3:-}
  [ -n "$effort" ] && [ "$effort" != default ] || return 0
  case "$harness" in
    claude)
      case "$effort" in
        low|medium|high|xhigh|max) printf -- '--effort %s ' "$(fm_profile_shell_quote "$effort")" ;;
      esac
      ;;
    codex)
      # The installed codex config schema uses model_reasoning_effort, and the
      # bundled model catalog advertises low|medium|high|xhigh. Omit max rather
      # than passing an unsupported value.
      case "$effort" in
        low|medium|high|xhigh) printf -- '-c %s ' "$(fm_profile_shell_quote "model_reasoning_effort=\"$effort\"")" ;;
      esac
      ;;
    grok)
      # grok exposes both --effort and --reasoning-effort; firstmate's profile
      # axis is the reasoning knob. As of grok 0.2.99, --reasoning-effort accepts
      # only low|medium|high and rejects both xhigh and max, so omit those rather
      # than passing a known-bad value.
      case "$effort" in
        low|medium|high) printf -- '--reasoning-effort %s ' "$(fm_profile_shell_quote "$effort")" ;;
      esac
      ;;
    agy)
      # agy 1.2.0 --effort accepts exactly low|medium|high, so xhigh and max are
      # omitted rather than passed as known-bad values (record-and-omit).
      case "$effort" in
        low|medium|high) printf -- '--effort %s ' "$(fm_profile_shell_quote "$effort")" ;;
      esac
      ;;
    pi|pi-signed)
      # Pi 0.80.6 accepts the full shared effort vocabulary, including max, through
      # its --thinking flag.
      case "$effort" in
        ultra)
          "$SCRIPT_DIR/fm-harness.sh" validate-native-effort "$harness" "$model" "$effort" || return 1
          printf -- '--codex-effort %s ' "$(fm_profile_shell_quote ultra)"
          ;;
        low|medium|high|xhigh|max) printf -- '--thinking %s ' "$(fm_profile_shell_quote "$effort")" ;;
      esac
      ;;
    omp)
      # omp 18.1.11 --thinking accepts off|minimal|low|medium|high|xhigh|max|auto,
      # a superset of the shared vocabulary, so every level maps straight across.
      case "$effort" in
        low|medium|high|xhigh|max) printf -- '--thinking %s ' "$(fm_profile_shell_quote "$effort")" ;;
      esac
      ;;
    muse)
      # muse 0.1.0-R708.1 --reasoning-effort accepts none|minimal|low|medium|
      # high|xhigh|ultra and defaults to high, so low..xhigh map straight across.
      # ultra is muse's max-CLASS level, so firstmate's max maps onto it - but
      # only ever as an EXPLICIT captain choice, never as a fallback, because
      # AGENTS.md section 4 forbids selecting max without captain preference and
      # the omitted effort here leaves muse on its own high default. muse's extra
      # none/minimal levels sit below firstmate's shared vocabulary and are
      # deliberately unreachable rather than remapped onto low.
      case "$effort" in
        low|medium|high|xhigh) printf -- '--reasoning-effort %s ' "$(fm_profile_shell_quote "$effort")" ;;
        max) printf -- '--reasoning-effort %s ' "$(fm_profile_shell_quote ultra)" ;;
      esac
      ;;
    # rovo has no --effort flag on `run`; its effort mapping rides
    # --config-override, but that flag is single-value (see
    # rovo_config_override_flag below) so it is built there, merged with the
    # mandatory allowedExternalPaths grant, rather than here.
    # opencode's interactive `opencode --prompt` launch has a verified --model
    # flag but no verified effort flag. Its `opencode run --variant` flag belongs
    # to a different, non-interactive launch mode, so fm-spawn does not pass it.
    # kimi likewise has no reasoning-effort flag; the requested axis stays in
    # task metadata but never reaches the launch command. Cursor encodes effort
    # in model ids such as cursor-grok-4.5-high, so it also receives no separate
    # effort flag.
  esac
}

# Workflow assignments must not silently discard an explicitly selected axis.
# Validate against the actual launch flag mapping, not a separate support table.
fm_validate_workflow_profile() {
  local harness=$1 model=$2 effort=$3 flags
  case "$harness" in claude|codex) ;; *)
    echo "error: workflow assignments require FirstMate Claude or Codex harness selection" >&2
    return 1 ;;
  esac
  [[ "$model" =~ ^[A-Za-z0-9][A-Za-z0-9._:/@+-]{0,255}$ ]] || {
    echo "error: workflow model must be a concrete harness model token or default" >&2; return 1;
  }
  case "$effort" in default|low|medium|high|xhigh|max|ultra) ;; *)
    echo "error: workflow effort is outside FirstMate's profile vocabulary" >&2; return 1 ;;
  esac
  if [ "$model" != default ]; then
    flags=$(model_flag_for_harness "$harness" "$model") || return 1
    [ -n "$flags" ] || { echo "error: explicit workflow model would be omitted" >&2; return 1; }
  fi
  if [ "$effort" != default ]; then
    flags=$(effort_flag_for_harness "$harness" "$effort" "$model") || return 1
    [ -n "$flags" ] || { echo "error: explicit workflow effort would be omitted for $harness: $effort" >&2; return 1; }
  fi
}
