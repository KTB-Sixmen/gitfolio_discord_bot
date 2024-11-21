from fastapi import APIRouter, Request, HTTPException
from discord import Embed, Color, HTTPException
from datetime import datetime
from bot import bot

sentry_router = APIRouter()

@sentry_router.post("/webhook/sentry")
async def webhook(request: Request):
    try:
        data = await request.json()
        event = data.get('event', {})
        project = data.get('project', 'Unknown Project')
        
        # Discord 임베드 메시지 생성
        embed = Embed(
            title=f"🚨 New Error in {project}",
            color=Color.red()
        )
        
        # 에러 메시지
        if 'message' in event:
            embed.add_field(
                name="Message", 
                value=event['message'][:1024],  # Discord 필드 길이 제한
                inline=False
            )
        
        # 예외 정보
        if 'exception' in event:
            exception = event['exception']['values'][0]
            embed.add_field(
                name="Type",
                value=exception.get('type', 'Unknown'),
                inline=True
            )
            embed.add_field(
                name="Value",
                value=exception.get('value', 'No details')[:1024],
                inline=True
            )
            
            # 스택트레이스 정보
            if 'stacktrace' in exception:
                frames = exception['stacktrace'].get('frames', [])
                # 마지막 3개의 프레임만 선택
                relevant_frames = frames[-3:]
                
                stack_info = []
                for frame in relevant_frames:
                    filename = frame.get('filename', 'unknown')
                    lineno = frame.get('lineno', '?')
                    function = frame.get('function', 'unknown')
                    stack_info.append(f"• {filename}:{lineno} in {function}")
                
                if stack_info:
                    stack_text = '\n'.join(stack_info)
                    # Discord 필드 길이 제한 고려
                    if len(stack_text) > 1024:
                        stack_text = stack_text[:1021] + "..."
                    embed.add_field(
                        name="Stacktrace",
                        value=f"```{stack_text}```",
                        inline=False
                    )
        
        # 사용자 정보
        if 'user' in event:
            user = event['user']
            user_info = []
            if 'id' in user:
                user_info.append(f"ID: {user['id']}")
            if 'email' in user:
                user_info.append(f"Email: {user['email']}")
            if 'username' in user:
                user_info.append(f"Username: {user['username']}")
            if user_info:
                embed.add_field(
                    name="User",
                    value='\n'.join(user_info),
                    inline=False
                )
        
        # 에러 URL
        if 'url' in data:
            embed.url = data['url']
        
        # 환경 정보
        if 'environment' in event:
            embed.add_field(
                name="Environment",
                value=event['environment'],
                inline=True
            )
            
        # 추가 태그 정보
        if 'tags' in event:
            tags_info = []
            for key, value in event['tags'].items():
                tags_info.append(f"{key}: {value}")
            if tags_info:
                embed.add_field(
                    name="Tags",
                    value='\n'.join(tags_info[:5]),  # 상위 5개 태그만 표시
                    inline=True
                )
        
        # 타임스탬프 (Discord.py 2.0에서는 datetime 객체를 직접 사용)
        embed.timestamp = datetime.now()
        
        # 푸터에 이벤트 ID 추가
        if 'event_id' in event:
            embed.set_footer(text=f"Event ID: {event['event_id']}")
        
        # Discord로 전송
        if bot.channel:
            try:
                await bot.channel.send(embed=embed)
                return {"status": "success", "message": "Error notification sent to Discord"}
            except HTTPException as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to send message to Discord: {str(e)}"
                )
        else:
            raise HTTPException(
                status_code=500,
                detail="Discord channel not initialized"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing webhook: {str(e)}"
        )
