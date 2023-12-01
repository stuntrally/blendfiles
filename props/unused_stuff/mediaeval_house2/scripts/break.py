from bge import logic

cont=logic.getCurrentController()
owner=cont.owner
col=cont.sensors['collision']
dur=owner['durability']
linV=owner.localLinearVelocity

if col.positive and (linV[0])+(linV[1])+(linV[2])>dur:
    owner['broken']=True