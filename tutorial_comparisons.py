"""Original visual comparisons for the public beginner lesson."""

EXAMPLES = {
 'identity': ('compare-identity-v1.webp', 'A · 설정이 바뀐 예시', 'A · Changed design', 'B · 기준 의상·머리 유지', 'B · Reference outfit and hair', '머리 길이, 티아라, 드레스의 색과 소매부터 비교하세요.', 'Compare hair length, tiara, gown color and sleeves first.'),
 'reference': ('character-sheet-duchess20-v3-center-soft-wm.webp', '전신 · 의상 확인', 'Full body · Check clothes', '얼굴 · 기준으로 저장', 'Portrait · Save as reference', '기준 시트에서 얼굴이 잘 보이는 컷을 골라 다음 생성에 첨부합니다.', 'Choose a clear portrait from the sheet and attach it to the next generation.'),
 'views': ('compare-views-v1.webp', 'A · 정면 전신', 'A · Front view', 'B · 측면 전신', 'B · Side view', '같은 드레스의 실루엣과 머리 길이가 다른 각도에서도 이어지는지 봅니다.', 'Check that the gown silhouette and hair length carry through both angles.'),
 'crop': ('compare-crop-v1.webp', 'A · 머리·신발 잘림', 'A · Head and shoes cropped', 'B · 전신과 여백 확보', 'B · Full body with margins', '전신 컷은 티아라 끝부터 구두까지 확인할 여백이 필요합니다.', 'A full-body reference needs enough room to check the tiara and shoes.'),
 'scene': ('compare-scene-v1.webp', 'A · 스튜디오 기준 컷', 'A · Studio reference', 'B · 성 안의 장면', 'B · Castle scene', '공간을 바꿔도 얼굴·머리·의상이 유지되는지 나란히 확인하세요.', 'Compare identity, hair and costume side by side after changing the setting.'),
 'direction': ('compare-direction-v1.webp', 'A · 부드러운 정면광', 'A · Soft front light', 'B · 왼쪽 측면광', 'B · Light from the left', '코와 볼의 그림자 방향을 보면 빛이 어디서 오는지 읽을 수 있습니다.', 'Read the nose and cheek shadows to identify the direction of the light.'),
 'contrast': ('compare-contrast-v1.webp', 'A · 보조광 많음', 'A · More fill', 'B · 보조광 적음', 'B · Less fill', '주광 방향을 유지한 채 어두운 쪽 볼의 밝기만 비교합니다.', 'Hold the key direction fixed and compare the brightness of the shadow-side cheek.'),
 'temperature': ('compare-temperature-v1.webp', 'A · 중립적인 빛', 'A · Neutral light', 'B · 차가운 창빛·따뜻한 촛불', 'B · Cool window, warm candle', '피부를 과하게 물들이지 않고, 창빛과 배경 촛불의 색 차이로 분위기를 만듭니다.', 'Build mood through the window and candle colors without heavily tinting the skin.'),
 'framing': ('character-lighting-duchess20-v3-center-soft-wm.webp', 'A · 기준 구도', 'A · Reference framing', 'B · 구도 유지, 조명 변경', 'B · Same framing, new light', '머리 크기·시선·카메라 높이가 비슷해야 조명 차이를 비교하기 쉽습니다.', 'Match head size, gaze and camera height to make lighting differences easier to read.'),
}

def render(key, t):
    image,ako,aen,bko,ben,ko,en=EXAMPLES[key]
    src='/assets/notes/'+image
    alt=t(ako+' / '+bko, aen+' / '+ben)
    return f'''<figure class="tutorial-comparison" data-comparison="{key}"><a href="{src}" target="_blank" rel="noopener" aria-label="{alt}"><img src="{src}" width="1536" height="1024" alt="{alt}" loading="lazy" decoding="async"></a><figcaption><div class="comparison-labels"><span>{t(ako,aen)}</span><span>{t(bko,ben)}</span></div><p>{t(ko,en)}</p></figcaption></figure>'''
