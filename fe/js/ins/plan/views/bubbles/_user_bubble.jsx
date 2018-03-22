const UserBubble = (props) => (
  <div
    className="m-user-bubble"
    key={props.key || 0}>
    <div className="bd">
      <div className="wrap">
        {props.children}
      </div>
    </div>
  </div>
)

export default UserBubble
